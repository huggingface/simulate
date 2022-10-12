# Copyright 2022 The HuggingFace Authors.
# Copyright (c) 2019 Sergey Krilov
# Copyright (c) 2018 Luke Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Lint as: python3
import base64
import mimetypes
import struct
from abc import ABC, abstractmethod
from os import path
from typing import Optional
from urllib.parse import quote

from .utils import create_parent_dirs


(GLB_JSON_CHUNK_TYPE,) = struct.unpack("<I", b"JSON")
(GLB_BINARY_CHUNK_TYPE,) = struct.unpack("<I", b"BIN\x00")


class GLTFResource(ABC):
    """
    Base class for a GLTF resource representation containing binary data. Note that depending on the resource type, the
    data may or may not actually be available to be consumed directly.
    """

    def __init__(self, uri: Optional[str] = None, data: Optional[bytes] = None):
        self._uri = uri
        self._data = data

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def data(self) -> Optional[bytes]:
        return self._data

    @data.setter
    def data(self, data: bytes):
        self._data = data

    @abstractmethod
    def clone(self) -> "GLTFResource":
        pass


class FileResource(GLTFResource):
    """
    GLTF resource that exists on the local filesystem. When exporting a GLTF model, all file resources will be saved to
    disk. When loading a GLTF model with load_file_resources set to True, any URIs that refer to a file will be imported
    as file resources.
    """

    def __init__(
        self,
        filename: Optional[str] = None,
        basepath: Optional[str] = None,
        autoload: bool = False,
        data: Optional[bytes] = None,
        mimetype: Optional[str] = None,
    ):
        super(FileResource, self).__init__(quote(filename), data)
        self._filename = filename
        self._loaded = self._data is not None
        self._basepath = basepath
        self._mimetype = mimetype
        if autoload:
            self.load()

    def __repr__(self) -> str:
        return f'FileResource("{self._filename}")'

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def mimetype(self) -> Optional[str]:
        return self._mimetype

    @property
    def fullpath(self) -> str:
        return path.join(self._basepath, self._filename) if self._basepath is not None else self._filename

    def load(self, force_reload: bool = False):
        if self._loaded and not force_reload:
            return
        if not self._filename:
            raise ValueError("Attempted to load FileResource without filename")
        filename = path.join(self._basepath, self._filename) if self._basepath is not None else self._filename
        with open(filename, "rb") as f:
            self._data = f.read()
            self._mimetype = self._mimetype or mimetypes.guess_type(filename)[0]
        self._loaded = True

    def export(self, basepath: Optional[str] = None) -> str:
        if not self._filename:
            raise ValueError("Attempted to export FileResource without filename")
        self.load()
        if self._data is None:
            raise ValueError("Attempted to export FileResource without data")
        basepath = basepath if basepath is not None else self._basepath
        filename = path.join(basepath, self._filename) if basepath is not None else self._filename
        create_parent_dirs(filename)
        with open(filename, "wb") as f:
            f.write(self._data)
        return filename

    def clone(self) -> "FileResource":
        return FileResource(self._filename, self._basepath, False, self._data, self._mimetype)


class ExternalResource(GLTFResource):
    """
    External GLTF resource referenced by URI. These resources are assumed to exist, and will not be loaded when
    importing or saved when exporting.
    """

    def __init__(self, uri: str):
        super(ExternalResource, self).__init__(uri)

    def __repr__(self) -> str:
        return f"FileResource({self.uri})"

    @property
    def data(self):
        raise ValueError("Data is not accessible for an external GLTF resource")

    @property
    def uri(self) -> str:
        return self._uri

    @uri.setter
    def uri(self, value: str):
        self._uri = value

    def clone(self) -> "ExternalResource":
        return ExternalResource(self.uri)


class GLBResource(GLTFResource):
    """
    Embedded GLTF resource inside a Binary glTF (GLB).
    """

    def __init__(self, data: bytes, resource_type: int = GLB_BINARY_CHUNK_TYPE):
        super(GLBResource, self).__init__(None, data)
        self._resource_type = resource_type

    @property
    def resource_type(self):
        return self._resource_type

    def clone(self) -> "GLBResource":
        return GLBResource(self.data, self._resource_type)


class Base64Resource(GLTFResource):
    """
    Base64-encoded resource embedded directly inside a JSON-based (non-binary) glTF model.
    """

    def __init__(self, data: bytes, mime_type: str = "application/octet-stream"):
        encoded_data = base64.b64encode(data).decode("utf-8")
        datauri = f"data:{mime_type};base64,{encoded_data}"
        super(Base64Resource, self).__init__(datauri, data)
        self.mime_type = mime_type

    @staticmethod
    def from_uri(uri: str) -> "Base64Resource":
        prefix, urlpath = uri.split(":", 1)
        if prefix != "data":
            raise ValueError(
                f'Invalid Data URI (must have a "data:" prefix). ' f'First 50 chars of Data URI follow: "{uri[:50]}"'
            )
        header, encoded_data = urlpath.split(",", 1)
        mime_type, encoding = header.split(";", 1)
        if encoding != "base64":
            raise RuntimeError(
                f'Unsupported encoding scheme in embedded data URI: "{encoding}". '
                f'Only "base64" encoding is supported.'
            )
        data = base64.b64decode(encoded_data)
        return Base64Resource(data, mime_type)

    def __repr__(self) -> str:
        return f"Base64Resource({len(self.data)} bytes)"

    def clone(self) -> "Base64Resource":
        return Base64Resource(self.data, self.mime_type)
