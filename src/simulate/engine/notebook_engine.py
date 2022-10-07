# Copyright 2022 The HuggingFace Authors and trimesh authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" A notebook plotting engine using three.js

Adapted from the "notebook.py" file of trimesh which render objects in HTML
and jupyter notebooks by saving them in gltf and loading the gltf with three.js
"""
import base64
import os
import typing
import zipfile
from io import BytesIO, StringIO
from typing import IO, Any, Dict, Optional, Union

from ..utils import logging
from .engine import Engine


if typing.TYPE_CHECKING:
    from ..scene import Scene


logger = logging.get_logger(__name__)
VIEWER_TEMPLATE = os.path.join(os.path.dirname(__file__), "notebook_viewer.zip")


def in_notebook() -> bool:
    """
    Check to see if we are in an IPython or Jupyter notebook.

    Returns:
        in_notebook (`bool`): Returns True if we are in a notebook.
    """
    try:
        # function returns IPython context, but only in IPython
        ipy = get_ipython()  # NOQA
        # we only want to render rich output in notebooks
        # in terminals we definitely do not want to output HTML
        name = str(ipy.__class__).lower()
        terminal = "terminal" in name

        # spyder uses ZMQshell, and can appear to be a notebook
        spyder = "_" in os.environ and "spyder" in os.environ["_"]

        # assume we are in a notebook if we are not in
        # a terminal, and we haven't been run by spyder
        notebook = (not terminal) and (not spyder)

        return notebook

    except BaseException as e:
        logger.error(f"Not in a notebook: {e}")
        return False


def wrap_as_stream(item: Union[bytes, str]) -> Union[BytesIO, StringIO]:
    """
    Wrap a string or bytes object as a file object.

    Args:
        item (`str` or `bytes`): Item to be wrapped.

    Returns:
        wrapped (`StringIO` or `BytesIO`): Contains data from item
    """
    if isinstance(item, str):
        return StringIO(item)
    elif isinstance(item, bytes):
        return BytesIO(item)
    raise ValueError(f"{type(item).__name__} cannot be wrapped!")


def decompress(file_obj: IO, file_type: str) -> Dict:
    """
    Given an open file object and a file type, return all components
    of the archive as open file objects in a dict.

    Args:
        file_obj (`file-like`):
            Containing compressed data
        file_type (`str`):
            File extension, 'zip', 'tar.gz', etc

    Returns:
        decompressed (`Dict`): Data from archive in format {file name : file-like}
    """

    def is_zip():
        archive = zipfile.ZipFile(file_obj)
        result = {name: wrap_as_stream(archive.read(name)) for name in archive.namelist()}
        return result

    def is_tar():
        import tarfile

        archive = tarfile.open(fileobj=file_obj, mode="r")
        result = {name: archive.extractfile(name) for name in archive.getnames()}
        return result

    file_type = str(file_type).lower()
    if isinstance(file_obj, bytes):
        file_obj = wrap_as_stream(file_obj)

    if file_type[-3:] == "zip":
        return is_zip()
    if "tar" in file_type[-6:]:
        return is_tar()
    raise ValueError("Unsupported type passed!")


class NotebookEngine(Engine):
    """
    API to run simulations in Notebooks.

    Args:
        scene (`Scene`):
            The scene to simulate.
        auto_update (`bool`, *optional*, defaults to `True`):
            Whether to automatically update the scene when an asset is updated.
    """

    def __init__(
        self,
        scene: "Scene",
        auto_update: Optional[bool] = False,
        **plotter_kwargs,
    ):
        super().__init__(scene, auto_update=auto_update)
        with open(VIEWER_TEMPLATE, "rb") as f:
            self._template = decompress(f, file_type="zip")["viewer.html.template"].read().decode("utf-8")

    def show(self, height: Optional[int] = 500, **plotter_kwargs) -> Any:
        """
        Show the scene in a notebook.

        Args:
            height (`int`, *optional*, defaults to `500`):
                The height of the viewer.
        """
        # keep as soft dependency
        from IPython import display

        # get export as bytes
        data = self._scene.as_glb_bytes()
        # encode as base64 string
        encoded = base64.b64encode(data).decode("utf-8")
        # replace keyword with our scene data
        as_html = self._template.replace("$B64GLTF", encoded)

        # escape the quotes in the HTML
        srcdoc = as_html.replace('"', "&quot;")
        # embed this puppy as the srcdoc attr of an IFrame
        # I tried this a dozen ways and this is the only one that works
        # display.IFrame/display.Javascript really, really don't work
        # div is to avoid IPython's pointless hardcoded warning
        embedded = display.HTML(
            " ".join(
                [
                    '<div><iframe srcdoc="{srcdoc}"',
                    'width="100%" height="{height}px"',
                    'style="border:none;"></iframe></div>',
                ]
            ).format(srcdoc=srcdoc, height=height)
        )
        return embedded
