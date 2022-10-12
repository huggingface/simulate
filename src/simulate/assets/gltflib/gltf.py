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
import codecs
import copy
import io
import struct
import warnings
from os import path
from typing import BinaryIO, Iterable, Iterator, List, Optional, Set, Tuple, Union
from urllib.parse import unquote, urlparse

from ...utils import logging
from .gltf_resource import (
    GLB_BINARY_CHUNK_TYPE,
    GLB_JSON_CHUNK_TYPE,
    Base64Resource,
    ExternalResource,
    FileResource,
    GLBResource,
    GLTFResource,
)
from .models import Buffer, BufferView, GLTFModel, Image
from .utils import create_parent_dirs, padbytes


logger = logging.get_logger(__name__)


class GLTF:
    GLB_HEADER_BYTELENGTH = 12

    def __init__(self, model: GLTFModel = None, resources: List[GLTFResource] = None):
        self.model = model
        self.resources = resources

    @classmethod
    def load(
        cls: "GLTF",
        filename: str,
        load_file_resources: bool = False,
        resources: Optional[List[GLTFResource]] = None,
        encoding: Optional[str] = None,
    ) -> "GLTF":
        """
        Loads a GLTF or GLB model from a filename. The model format will be inferred from the filename extension.
        :param filename: Path to the GLTF or GLB file
        :param load_file_resources: If True, external file resources that are not provided via the "resources"
            array will be loaded from the filesystem. The paths are assumed to be relative to the GLTF file.
        :param resources: Optional list of preloaded resources. Any resources referenced in the GLTF file that are
            present in the resources array will be used instead of loading those resources from the external
            source.
        :param encoding: File encoding (if known) of the glTF file (if reading gltf), or the JSON block within the
            GLB (if reading glb). Per the spec, glTF should use UTF-8 without BOM for JSON data. However, to accommodate
            working with models that do not fully adhere to the spec, the file may be read with a different encoding.
            If not passed in, the encoding will be guessed from one of several supported encodings (based on BOM),
            defaulting to UTF-8 if it cannot be inferred.
        :return: GLTF instance
        """
        ext = path.splitext(filename)[1].lower()
        if ext == ".gltf":
            return cls.load_gltf(filename, load_file_resources, resources, encoding)
        elif ext == ".glb":
            return cls.load_glb(filename, load_file_resources, resources, encoding)
        raise RuntimeError(
            f"File format could not be inferred from filename: {filename}. Ensure the filename has "
            f"the appropriate extension (.gltf or .glb), or call load_gltf or load_glb directly if "
            f"the filename does not follow the convention but the format is known."
        )

    @classmethod
    def load_gltf(
        cls: "GLTF",
        filename: str,
        load_file_resources: bool = False,
        resources: Optional[List[GLTFResource]] = None,
        encoding: Optional[str] = None,
    ) -> "GLTF":
        """
        Loads a model in GLTF format from a filename
        :param filename: Path to the GLTF file
        :param load_file_resources: If True, external file resources that are not provided via the "resources"
            array will be loaded from the filesystem. The paths are assumed to be relative to the GLTF file.
        :param resources: Optional list of preloaded resources. Any resources referenced in the GLTF file that are
            present in the resources array will be used instead of loading those resources from the external
            source.
        :param encoding: File encoding (if known). Per the spec, glTF should use UTF-8 without BOM. However, to
            accommodate working with models that do not fully adhere to the spec, the file may be read with a different
            encoding. If not passed in, the encoding will be guessed from one of several supported encodings (based on
            BOM), defaulting to UTF-8 if it cannot be inferred.
        :return: GLTF instance
        """
        gltf = GLTF(model=None, resources=resources)
        with open(filename, "rb") as f:
            data = f.read()
            json = GLTF._decode_bytes(data, encoding)
            gltf.model = GLTFModel.from_json(json)
        basepath = path.dirname(filename)
        gltf._load_resources(basepath, load_file_resources)
        return gltf

    @classmethod
    def load_glb(
        cls: "GLTF",
        filename: str,
        load_file_resources: bool = False,
        resources: Optional[List[GLTFResource]] = None,
        encoding: Optional[str] = None,
    ) -> "GLTF":
        """
        Loads a model in GLB format from a filename
        :param filename: Path to the GLB file
        :param load_file_resources: If True, external file resources that are not provided via the "resources"
            array will be loaded from the filesystem. The paths are assumed to be relative to the GLTF file.
        :param resources: Optional list of preloaded resources. Any resources referenced in the GLTF file that are
            present in the resources array will be used instead of loading those resources from the external
            source.
        :param encoding: File encoding (if known) of the JSON chunk within the GLB. Per the spec, JSON data should be
            encoded using UTF-8 (without BOM). However, to accommodate working with models that do not fully adhere to
            the spec, the JSON chunk may be read with a different encoding. If not passed in, the encoding will be
            guessed from one of several supported encodings (based on BOM), defaulting to UTF-8 if cannot be inferred.
        :return: GLTF instance
        """
        gltf = GLTF(model=None, resources=resources)
        with open(filename, "rb") as f:
            gltf._load_glb(f, encoding)
        basepath = path.dirname(filename)
        gltf._load_resources(basepath, load_file_resources)
        return gltf

    @property
    def glb_resources(self) -> List[GLBResource]:
        return [resource for resource in self.resources if isinstance(resource, GLBResource)]

    def export(self, filename: str, save_file_resources: bool = True) -> Union[List[str], "GLTF"]:
        """
        Exports the model to a GLTF or GLB (inferred from filename extension).
        :param filename: Output filename
        :param save_file_resources: If True, external file resources present in the resources list will be saved
        :return Exported GLTF instance. This instance will be distinct from the original GLTF instance (which will not
            be mutated) since the resources and associated buffers and buffer views may potentially change if the
            resources become embedded (e.g., when converting from GLTF to GLB).
        """
        ext = path.splitext(filename)[1].lower()
        if ext == ".gltf":
            return self.export_gltf(filename, save_file_resources)
        elif ext == ".glb":
            return self.export_glb(
                filename,
                embed_buffer_resources=True,
                embed_image_resources=True,
                save_file_resources=save_file_resources,
            )
        raise RuntimeError(
            f"File format could not be inferred from filename: {filename}. Ensure the filename has "
            f"the appropriate extension (.gltf or .glb), or call export_gltf or export_glb directly."
        )

    def export_gltf(self, filename: str, save_file_resources: bool = True) -> List[str]:
        """
        Exports the model to a GLTF file
        :param filename: Output filename
        :param save_file_resources: If True, external file resources present in the resources list will be saved
        :return List of paths to the saved files (glTF + resources).
        """
        gltf = self.clone()
        # noinspection PyProtectedMember
        file_names = gltf._export_gltf(filename, save_file_resources)
        return file_names

    def export_glb(
        self,
        filename: str,
        embed_buffer_resources: bool = True,
        embed_image_resources: bool = True,
        save_file_resources: bool = True,
    ) -> "GLTF":
        """
        Exports the model to a GLB file
        :param filename: Output filename
        :param embed_buffer_resources: If True, buffer resources will be embedded in the GLB. The default value is True.
            Note that only file and data URI resources will be converted. External network resources will be left as
            they are. Note: If there are any buffers that use file resources which you wish to leave as external file
            references, set this to False and convert the resources individually before calling export_glb.
        :param embed_image_resources: If True, image resources will be embedded in the GLB. The default value is True.
            Note that only file and data URI resources will be converted. External network resources will be left as
            they are. Note: If there are any images that use file resources which you wish to leave as external file
            references, set this to False and convert the resources individually before calling export_glb.
        :param save_file_resources: If True, any external file resources that are not being embedded in the GLB
            will be saved (in addition to the main GLB file). The default value is True.
        :return Exported GLTF instance. This instance will be distinct from the original GLTF instance (which will not
            be mutated) since the resources and associated buffers and buffer views may potentially change if the
            resources become embedded (e.g., when converting from GLTF to GLB).
        """
        glb = self.clone()
        # noinspection PyProtectedMember
        glb._export_glb(filename, embed_buffer_resources, embed_image_resources, save_file_resources)
        return glb

    def as_glb_bytes(self) -> bytes:
        """
        Return the model as a GLB bytes
        :return the model as GLB bytes.

        The original GLTF instance is NOT mutated
        (in particular resources and associated buffers and buffer views are not modified to become embedded).
        """
        glb = self.clone()
        # noinspection PyProtectedMember
        return glb._as_glb_bytes()

    def clone(self) -> "GLTF":
        """
        Clones the model and its resources to a new instance.
        :return: Cloned model
        """
        model = copy.deepcopy(self.model)
        resources = None if self.resources is None else [resource.clone() for resource in self.resources]
        return GLTF(model, resources)

    def get_resource(self, uri: str, strict: bool = False) -> GLTFResource:
        next_item = next(
            (
                resource
                for resource in (self.resources or [])
                if uri
                in (
                    {resource.uri}
                    if not isinstance(resource, FileResource) or strict
                    else {resource.uri, resource.filename}
                )
            ),
            None,
        )
        if next_item is None:
            raise ValueError(f"Cannot find resource with uri {uri}.")
        return next_item

    def get_glb_resource(self, resource_type: int = GLB_BINARY_CHUNK_TYPE) -> Optional[GLBResource]:
        for resource in self.glb_resources:
            if resource.resource_type == resource_type:
                return resource

    def get_glb_resources_of_type(self, resource_type: int) -> List[GLBResource]:
        return [resource for resource in self.glb_resources if resource.resource_type == resource_type]

    def remove_resource_by_uri(self, uri: str):
        resource = self.get_resource(uri)
        if resource is not None:
            self.resources.remove(resource)

    def embed_resource(self, resource: GLTFResource) -> GLBResource:
        """
        Embeds a given resource, converting it to a GLBResource. If the model already contains a GLBResource, then the
        resource data will be appended to the existing GLBResource. Any buffers and buffer views that refer to the
        original resource will be modified to point to the embedded GLBResource instead.
        :param resource: Resource to embed. This may be a FileResource or a Base64Resource (or a GLBResource, in which
            case it will simply be returned since it is already embedded). Note that embedding resources of type
            ExternalResource will result in an error since loading external resource data is not supported.
        :return: GLBResource
        """
        if resource not in (self.resources or []):
            raise ValueError("Resource to embed must be present in the resources list")
        glb_resource = self.get_glb_resource()
        if resource is glb_resource:
            return glb_resource
        if isinstance(resource, ExternalResource):
            raise TypeError("Embedding an ExternalResource is not supported")
        if isinstance(resource, FileResource) and not resource.loaded:
            resource.load()
        if isinstance(resource, FileResource) or isinstance(resource, Base64Resource):
            data = bytearray(resource.data)
            glb_resource, offset, bytelen = self._create_or_extend_glb_resource(data)
            self.resources.remove(resource)
            self._update_model_after_embedding_resource(resource, offset, bytelen)
        return glb_resource

    def convert_to_file_resource(self, resource: GLTFResource, filename: str) -> FileResource:
        """
        Converts a given GLTFResource to a FileResource. Note the file will not be created until the model is saved
        (with save_file_resources flag set to true).

        If the resource is already a FileResource and the filename matches, no action is performed. If the filename is
        different, then the filename will be updated on any buffers and images that reference it.

        If the resource is a GLBResource or Base64Resource, it will be un-embedded and converted to an external file
        resource, and any buffers that reference the resource will be updated appropriately. Any embedded images that
        reference the resource will be updated. If the image previously referenced a buffer view, it will now reference
        a URI instead; the corresponding buffer view will be removed if no other parts of the model refer to it.
        Further, after removing the buffer view, if no other buffer views refer to the same buffer, then the buffer will
        be removed as well.

        If the resource is an ExternalResource, this method will raise an error (accessing external resource data is not
        supported).

        :param resource: Resource to convert.
        :param filename: Filename to use for the external file resource when saving the model.
        :return: Converted FileResource
        """
        if resource not in (self.resources or []):
            raise RuntimeError(f'Resource with URI "{resource.uri}" was not found in the model.')
        if isinstance(resource, FileResource):
            if resource.filename == filename:
                return resource
            resource.load()
            file_resource = FileResource(filename, data=resource.data, mimetype=resource.mimetype)
            self._update_model_resources_by_uri(resource.uri, file_resource.uri)
            if resource.uri != resource.filename:
                self._update_model_resources_by_uri(resource.filename, file_resource.uri)
            self.resources[self.resources.index(resource)] = file_resource
            return file_resource
        if isinstance(resource, Base64Resource):
            file_resource = FileResource(filename, data=resource.data, mimetype=resource.mime_type)
            self._update_model_resources_by_uri(resource.uri, file_resource.uri)
            self.resources[self.resources.index(resource)] = file_resource
            return file_resource
        if isinstance(resource, GLBResource):
            assert resource is self.get_glb_resource()
            # Replace the GLB resource with a file resource
            file_resource = FileResource(filename, data=resource.data)
            self.resources.remove(resource)
            self.resources.insert(0, file_resource)
            self._unembed_glb(filename)
            return file_resource
        if isinstance(resource, ExternalResource):
            # TODO: Maybe this should be allowed if exporting with save_file_resources set to False? In that case, we
            # don't need access to ExternalResource data.
            raise ValueError(
                "ExternalResource may not be converted to a FileResource (accessing ExternalResource "
                "data is not yet supported.)"
            )

    def convert_to_base64_resource(
        self, resource: GLTFResource, mime_type: str = "application/octet-stream"
    ) -> Base64Resource:
        """
        Converts a given GLTFResource to a Base64Resource.

        If the resource is already a Base64Resource, no action is performed.

        If the resource is a FileResource, then it will be converted to a Base64Resource. The data for the FileResource
        will be loaded from disk if not already loaded (which may raise an IOError if the file does not exist).

        If the resource is a GLBResource, it will be converted to a Base64Resource. The GLB buffer will be replaced with
        a buffer with a data URI (or removed entirely if it is only used by images). Any images that refer to the
        resource via a buffer view will instead refer to the image directly via a data URI, and the corresponding buffer
        view will be removed (if it is not also referenced elsewhere). Further, if no other buffer views refer to the
        same buffer as the removed buffer view, then the buffer will be removed entirely as well.

        If the resource is an ExternalResource, this method will raise an error (accessing external resource data is not
        supported).

        :param resource: Resource to convert.
        :param mime_type: MIME Type of the data (if known). Defaults to 'application/octet-stream'.
        :return: Converted Base64Resource
        """
        if resource not in (self.resources or []):
            raise RuntimeError(f'Resource with URI "{resource.uri}" was not found in the model.')
        if isinstance(resource, FileResource):
            resource.load()
            base64_resource = Base64Resource(resource.data, mime_type)
            self._update_model_resources_by_uri(resource.uri, base64_resource.uri)
            if resource.uri != resource.filename:
                self._update_model_resources_by_uri(resource.filename, base64_resource.uri)
            self.resources[self.resources.index(resource)] = base64_resource
            return base64_resource
        if isinstance(resource, Base64Resource):
            return resource
        if isinstance(resource, GLBResource):
            assert resource is self.get_glb_resource()
            # Replace the GLB resource with a Base64Resource
            base64_resource = Base64Resource(resource.data, mime_type)
            self.resources.remove(resource)
            self.resources.insert(0, base64_resource)
            self._unembed_glb(base64_resource.uri)
            return base64_resource
        if isinstance(resource, ExternalResource):
            raise ValueError(
                "ExternalResource may not be converted to a Base64Resource (accessing ExternalResource "
                "data is not yet supported, and is necessary to generate the Data URI.)"
            )

    def convert_to_external_resource(self, resource: GLTFResource, uri: str) -> ExternalResource:
        """
        Converts a given GLTFResource to an ExternalResource with the given URI. Note that this library does not handle
        calling out to external resources, so this is strictly a bookkeeping operation. It is the responsibility of the
        caller to ensure that the resource exists externally. Note when converting a resource to an ExternalResource,
        the resource data becomes inaccessible.

        If the resource is already an ExternalResource and the URI matches, no action is performed. If the URI is
        different, then the URI will be updated on the resource instance as well as on any corresponding buffers or
        images in the model.

        If the resource is a FileResource or Base64Resource, then it will be converted to an ExternalResource, and all
        buffers and images will be updated appropriately.

        If the resource is a GLBResource, it will be converted to an ExternalResource. The GLB buffer will be replaced
        with a buffer with a data URI (or removed entirely if it is only used by images). Any images that refer to the
        resource via a buffer view will instead refer to the image directly via a data URI, and the corresponding buffer
        view will be removed (if it is not also referenced elsewhere). Further, if no other buffer views refer to the
        same buffer as the removed buffer view, then the buffer will be removed entirely as well.

        :param resource: Resource to convert.
        :param uri: Resource URI
        :return: Converted Base64Resource
        """
        if resource not in (self.resources or []):
            raise RuntimeError(f'Resource with URI "{resource.uri}" was not found in the model.')
        if isinstance(resource, FileResource) or isinstance(resource, Base64Resource):
            external_resource = ExternalResource(uri)
            self._update_model_resources_by_uri(resource.uri, uri)
            if isinstance(resource, FileResource) and resource.uri != resource.filename:
                self._update_model_resources_by_uri(resource.filename, uri)
            self.resources[self.resources.index(resource)] = external_resource
            return external_resource
        if isinstance(resource, GLBResource):
            assert resource is self.get_glb_resource()
            # Replace the GLB resource with an external resource
            external_resource = ExternalResource(uri)
            self.resources.remove(resource)
            self.resources.insert(0, external_resource)
            self._unembed_glb(uri)
            return external_resource
        if isinstance(resource, ExternalResource):
            if resource.uri == uri:
                return resource
            self._update_model_resources_by_uri(resource.uri, uri)
            resource.uri = uri
            return resource

    @classmethod
    def _decode_bytes(cls: "GLTF", data: bytes, encoding: Optional[str] = None) -> str:
        if encoding is not None:
            return data.decode(encoding, errors="replace")
        elif data.startswith(codecs.BOM_UTF16_BE):
            return data.decode("utf-16-be", errors="replace").lstrip("\ufeff")
        elif data.startswith(codecs.BOM_UTF16_LE):
            return data.decode("utf-16-le", errors="replace").lstrip("\ufeff")
        else:
            # Decode using utf-8-sig (instead of utf-8) to handle UTF-8 with and without BOM.
            # If BOM is present, it will be automatically stripped out.
            return data.decode("utf-8-sig", errors="replace")

    def _load_resources(self, basepath: str, autoload: bool = False):
        self.resources = self.resources or []
        for uri in self._get_resource_uris_from_model():
            resource = _get_resource(uri, basepath, autoload)
            if resource is not None:
                self.resources.append(resource)

    def _validate_resources(self):
        for uri in self._get_resource_uris_from_model():
            resource = self.get_resource(uri)
            if resource is None:
                raise RuntimeError(f'Missing resource with uri: "{uri}".')

    def _export_file_resources(self, basepath: str) -> List[str]:
        file_names = []
        if self.resources is None or len(self.resources) == 0:
            return file_names
        for resource in self.resources:
            if isinstance(resource, FileResource):
                file_name_ressource = resource.export(basepath)
                file_names += file_name_ressource
        return file_names

    def _load_glb(self, f: BinaryIO, json_encoding: Optional[str] = None):
        self.resources = []
        bytelen = self._load_glb_header(f)
        self._load_glb_chunks(f, json_encoding)
        pos = f.tell()
        if pos != bytelen:
            warnings.warn(
                f"GLB file length specified in file header ({bytelen}) does not match number of bytes "
                f"read ({pos}). The GLB file may be corrupt.",
                RuntimeWarning,
            )

    def _load_glb_header(self, f: BinaryIO) -> int:
        b = f.read(self.GLB_HEADER_BYTELENGTH)
        magic = b[0:4]
        if magic != b"glTF":
            raise RuntimeError("File is not a valid GLB file")
        (version,) = struct.unpack_from("<I", b, 4)
        if version != 2:
            raise RuntimeError(f'Unsupported GLB file version: "{version}". Only version 2 is currently supported')
        (bytelen,) = struct.unpack_from("<I", b, 8)
        return bytelen

    def _load_glb_chunks(self, f: BinaryIO, json_encoding: Optional[str] = None):
        while self._load_glb_chunk(f, json_encoding):
            pass

    def _load_glb_chunk(self, f: BinaryIO, json_encoding: Optional[str] = None) -> bool:
        b = f.read(8)
        if b == b"":
            return False
        if len(b) != 8:
            raise RuntimeError(
                f"Unexpected EOF when processing GLB chunk header. Chunk header must be 8 bytes, "
                f"got {len(b)} bytes."
            )
        (chunk_length,) = struct.unpack_from("<I", b, 0)
        (chunk_type,) = struct.unpack_from("<I", b, 4)
        if chunk_type == GLB_JSON_CHUNK_TYPE:
            self._load_glb_json_chunk_body(f, chunk_length, json_encoding)
        else:
            self._load_glb_binary_chunk_body(f, chunk_type, chunk_length)
        return True

    def _load_glb_json_chunk_body(self, f: BinaryIO, bytelen: int, json_encoding: Optional[str] = None):
        if bytelen == 0:
            raise RuntimeError("JSON chunk may not be empty")
        b = f.read(bytelen)
        if len(b) != bytelen:
            warnings.warn("Unexpected EOF when parsing JSON chunk body. The GLB file may be corrupt.", RuntimeWarning)
        model_json = GLTF._decode_bytes(b, json_encoding)
        self.model = GLTFModel.from_json(model_json)

    def _load_glb_binary_chunk_body(self, f: BinaryIO, chunk_type: int, bytelen: int):
        b = f.read(bytelen)
        if len(b) != bytelen:
            warnings.warn(
                "Unexpected EOF when parsing binary chunk body. The GLB file may be corrupt.", RuntimeWarning
            )
        resource = GLBResource(b, chunk_type)
        self.resources.append(resource)

    def _export_gltf(self, filename: str, save_file_resources: bool = True) -> List[str]:
        if any(isinstance(resource, GLBResource) for resource in (self.resources or [])):
            raise TypeError(
                "Model may not contain resources of type GLBResource when exporting to GLTF. "
                "Convert the GLBResource to a FileResource, Base64Resource, or ExternalResource using the "
                "provided helper methods in this class (GLTF.convert_to_file_resource,"
                "GLTF.convert_to_base64_resource, or GLTF.convert_to_external_resource) prior to "
                "exporting to GLTF, or export to GLB instead."
            )
        create_parent_dirs(filename)
        data = self.model.to_json()
        file_names = [filename]
        logger.info(filename)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
        if save_file_resources:
            self._validate_resources()
            basepath = path.dirname(filename)
            file_names_resources = self._export_file_resources(basepath)
            file_names += file_names_resources
        return file_names

    def _export_glb(
        self,
        filename: str,
        embed_buffer_resources: bool = True,
        embed_image_resources: bool = True,
        save_file_resources: bool = True,
    ):
        if embed_buffer_resources:
            self._embed_buffer_resources()
        if embed_image_resources:
            self._embed_image_resources()
        create_parent_dirs(filename)
        with open(filename, "wb") as f:
            self._write_glb(f)
        if save_file_resources:
            self._validate_resources()
            basepath = path.dirname(filename)
            self._export_file_resources(basepath)

    def _as_glb_bytes(self) -> bytes:
        self._embed_buffer_resources()
        self._embed_image_resources()
        with io.BytesIO() as f:
            self._write_glb(f)
            return f.getvalue()

    def _get_resource_uris_from_model(self) -> Set:
        uris = set()
        if self.model.buffers is not None:
            uris.update([buffer.uri for buffer in self.model.buffers if buffer.uri is not None])
        if self.model.images is not None:
            uris.update(
                [image.uri for image in self.model.images if image.uri is not None and image.bufferView is None]
            )
        return uris

    def _get_buffers_by_uri(self, uri: str) -> Iterator[Tuple[int, Buffer]]:
        if self.model.buffers is None:
            return
        for i, buffer in enumerate(self.model.buffers):
            if buffer.uri == uri:
                yield i, buffer

    def _get_images_by_uri(self, uri: str) -> Iterator[Tuple[int, Image]]:
        if self.model.images is None:
            return
        for i, image in enumerate(self.model.images):
            if image.uri == uri:
                yield i, image

    def _update_model_resources_by_uri(self, old_uri: str, new_uri: str):
        for _, buffer in self._get_buffers_by_uri(old_uri):
            buffer.uri = new_uri
        for _, image in self._get_images_by_uri(old_uri):
            image.uri = new_uri

    def _write_glb(self, f: BinaryIO):
        self._prepare_glb()
        self._write_glb_header(f)
        self._write_glb_body(f)

    def _prepare_glb(self):
        json_bytes = bytearray(self.model.to_json(separators=(",", ":")).encode("utf-8"))
        json_len = padbytes(json_bytes, 4, b"\x20")
        json_chunk = (json_len, GLB_JSON_CHUNK_TYPE, json_bytes)
        self._chunks = [json_chunk]
        for resource in self.glb_resources:
            data = resource.data
            bytelen = len(data)
            if bytelen % 4 != 0:
                data = bytearray(data)
                bytelen = padbytes(data, 4)
            chunk = (bytelen, resource.resource_type, data)
            self._chunks.append(chunk)

    def _write_glb_header(self, f: BinaryIO):
        chunk_header_len = 8
        bytelen = self.GLB_HEADER_BYTELENGTH + sum(chunk[0] + chunk_header_len for chunk in self._chunks)
        output = bytearray()
        output.extend(b"glTF")
        output.extend(struct.pack("<I", 2))
        output.extend(struct.pack("<I", bytelen))
        f.write(output)

    def _write_glb_body(self, f: BinaryIO):
        for chunk in self._chunks:
            bytelen, chunk_type, data = chunk
            f.write(struct.pack("<I", bytelen))
            f.write(struct.pack("<I", chunk_type))
            f.write(data)

    def _embed_buffer_resources(self):
        if self.model.buffers is None:
            return

        enumerated_buffers = None
        while enumerated_buffers is None:
            enumerated_buffers = enumerate(iter(self.model.buffers))
            for i, buffer in enumerated_buffers:
                if buffer.uri is None:
                    continue

                resource = self.get_resource(buffer.uri)
                if resource is None:
                    raise RuntimeError(f'Missing resource: "{buffer.uri}" (referenced in buffer with index {i})')
                self.embed_resource(resource)

                # Restart enumeration since embedding resource may have removed more than one buffer
                enumerated_buffers = None
                break

    def _embed_image_resources(self):
        if self.model.images is None:
            return

        enumerated_images = None
        while enumerated_images is None:
            enumerated_images = enumerate(iter(self.model.images))
            for i, image in enumerated_images:
                if image.uri is None or image.bufferView is not None:
                    continue

                resource = self.get_resource(image.uri)
                if resource is None:
                    raise RuntimeError(f'Missing resource: "{image.uri}" (referenced in image with index {i})')
                self.embed_resource(resource)

                # Restart enumeration since embedding resource may have removed more than one image
                enumerated_images = None
                break

    def _get_glb_buffer(self) -> Optional[Buffer]:
        """
        Returns the GLB buffer if present. The GLB buffer must be the first in the list, and have its URI undefined.
        """
        if self.model.buffers is None or len(self.model.buffers) == 0:
            # There are no buffers in the model yet. Ensure there are no buffer views, as that would indicate an error.
            if self.model.bufferViews is not None and len(self.model.bufferViews) > 0:
                raise RuntimeError(
                    "Model contains a buffer view without a buffer. This is not valid and indicates "
                    "the model is likely corrupt."
                )
            return None
        first_buffer = self.model.buffers[0]
        if first_buffer.uri is None:
            # Validate all other buffers have a uri defined. Per the spec, the GLB embedded buffer must be the first in
            # the list. Issue a warning if this is not the case.
            for i, buffer in enumerate(self.model.buffers[1:]):
                if buffer.uri is None:
                    warnings.warn(
                        f"Buffer at index {i} has its uri undefined, but it is not the first buffer in the "
                        f"list. This is not valid per the specification. The GLB-stored buffer must be the "
                        f"first buffer in the buffers array.",
                        RuntimeWarning,
                    )
            return first_buffer
        return None

    def _get_or_create_glb_buffer(self) -> Buffer:
        glb_buffer = self._get_glb_buffer()
        if glb_buffer is not None:
            return glb_buffer
        # Create a GLB buffer
        if self.model.buffers is None:
            self.model.buffers = []
        glb_buffer = Buffer(byteLength=0)
        self.model.buffers.insert(0, glb_buffer)
        # Increment the buffer index on all existing buffer views by 1 to account for the newly-inserted buffer.
        if self.model.bufferViews is not None:
            for buffer_view in self.model.bufferViews:
                buffer_view.buffer += 1
        return glb_buffer

    def _create_or_extend_glb_resource(self, data: bytearray) -> Tuple[GLBResource, int, int]:
        bytelen = len(data)
        glb_resource = self.get_glb_resource()
        if glb_resource is None:
            offset = 0
            buffer_bytelen = padbytes(data, 4)
            glb_resource = GLBResource(data)
            self.resources.append(glb_resource)
        else:
            # Pad the data in the existing GLBResource to a multiple of 4 bytes
            existing_data = bytearray(glb_resource.data)
            offset = padbytes(existing_data, 4)
            # Merge new data with the data we already have in the existing GLBResource
            data[0:0] = existing_data
            # Re-pad the merged byte array
            buffer_bytelen = padbytes(data, 4)
            # Update the data on the existing GLBResource
            glb_resource.data = bytes(data)
        buffer = self._get_or_create_glb_buffer()
        buffer.byteLength = buffer_bytelen
        # Return the GLBResource, as well as the offset and bytelength of the inserted data
        return glb_resource, offset, bytelen

    def _embed_buffer_views(self, buffer_index: int, glb_offset: int):
        if self.model.bufferViews is not None:
            for buffer_view in self.model.bufferViews:
                if buffer_view.buffer == buffer_index:
                    buffer_view.buffer = 0
                    buffer_view.byteOffset = (buffer_view.byteOffset or 0) + glb_offset

    def _create_embedded_image_buffer_view(self, byte_offset: int, byte_length: int) -> int:
        buffer_view = BufferView(buffer=0, byteOffset=byte_offset, byteLength=byte_length)
        if self.model.bufferViews is None or len(self.model.bufferViews) == 0:
            self.model.bufferViews = [buffer_view]
            return 0
        self.model.bufferViews.append(buffer_view)
        return len(self.model.bufferViews) - 1

    def _update_model_after_embedding_resource(self, resource: GLTFResource, offset: int, bytelen: int):
        resource_uris = {resource.uri}
        if isinstance(resource, FileResource):
            resource_uris.add(resource.filename)
        if self.model.buffers is not None:
            enumerated_buffers = list(enumerate(self.model.buffers))
            for i, buffer in enumerated_buffers:
                if buffer.uri in resource_uris:
                    # Remove the buffer since it is now embedded
                    self.model.buffers.remove(buffer)
                    # Update any buffers views that point to this buffer
                    self._update_buffer_views_after_embedding_resource(i, offset)
                    # Decrement the buffer index on any buffer views that come after the removed buffer
                    if self.model.bufferViews is not None:
                        for buffer_view in self.model.bufferViews:
                            if buffer_view.buffer > i:
                                buffer_view.buffer -= 1
        if self.model.images is not None:
            for i, image in enumerate(self.model.images):
                if image.uri in resource_uris:
                    image.bufferView = self._create_embedded_image_buffer_view(offset, bytelen)
                    if isinstance(resource, Base64Resource):
                        image.uri = None
                        image.mimeType = resource.mime_type
                    elif isinstance(resource, FileResource):
                        image.uri = None
                        image.mimeType = resource.mimetype

    def _update_buffer_views_after_embedding_resource(self, buffer_index: int, offset: int):
        if self.model.bufferViews is not None:
            for buffer_view in self.model.bufferViews:
                if buffer_view.buffer == buffer_index:
                    buffer_view.buffer = 0
                    buffer_view.byteOffset = (buffer_view.byteOffset or 0) + offset

    def _unembed_glb(self, uri: str):
        """
        Replaces the GLB buffer with a regular buffer that has its URI set to a file or other external resource.
        Any images that referred to the GLB buffer are updated to simply reference a URL, and their corresponding
        buffer views are removed (if not referenced elsewhere). If the GLB buffer was only used by images, then it
        is removed entirely (rather than replaced with another buffer), and any buffer indices in the remaining buffer
        views are updated to reflect the removed buffer.
        """
        # Replace the GLB buffer with a regular buffer that has its URI set to the external file
        glb_buffer = self._get_glb_buffer()
        if glb_buffer is not None:
            self.model.buffers.remove(glb_buffer)
            buffer = Buffer(uri=uri, byteLength=glb_buffer.byteLength)
            self.model.buffers.insert(0, buffer)
            # Find all buffer views that refer to the GLB buffer
            buffer_view_indices = set()
            enumerated_buffer_views = list(enumerate(self.model.bufferViews or []))
            for i, buffer_view in enumerated_buffer_views:
                if buffer_view.buffer == 0:
                    buffer_view_indices.add(i)
            # Check if any of the buffers views that refer to the GLB buffer are referenced by anything other than
            # images. If the buffer view is only used by images, then we can set the URI on the image directly and
            # get rid of the buffer views entirely. Otherwise, we must keep the buffer view intact, and have the
            # image continue to reference the buffer view. Currently, the only entities that refer to buffer views
            # (other than images) are accessors (as well as their corresponding "sparse" sub-properties). It is
            # unlikely that both an image and an accessor would both reference the same buffer view, but in case
            # it does, we do not want to corrupt the model by removing a buffer view that is being referenced
            # elsewhere.
            accessor_buffer_view_indices = self._get_buffer_view_indices_used_by_accessors()
            if buffer_view_indices & accessor_buffer_view_indices:
                # Buffer view indices are in use by accessors, so must keep everything intact. Nothing more to do.
                return
            # Buffer views only used by images, so the buffer and the corresponding buffer views can be removed.
            # First remove the buffer and update the buffer indices on all remaining buffer views to account for the
            # removed buffer.
            self.model.buffers.pop(0)
            for buffer_view in self.model.bufferViews or []:
                if buffer_view.buffer > 0:
                    buffer_view.buffer -= 1
            # Find all images that reference the removed buffer views and update their URIs.
            for image in self.model.images or []:
                if image.bufferView in buffer_view_indices:
                    image.bufferView = None
                    image.uri = uri
            # Now remove the buffer views that referred to the GLB buffer. Any accessors and images that reference a
            # buffer view after the one that was removed need to be updated.
            self._remove_buffer_views_by_indices(buffer_view_indices)

    def _get_buffer_view_indices_used_by_accessors(self) -> Set:
        """
        Returns the unique set of buffer view indices that are referenced by accessors (or their sparse counterparts).
        """
        buffer_view_indices = set()
        for accessor in self.model.accessors or []:
            if accessor.bufferView is not None:
                buffer_view_indices.add(accessor.bufferView)
            if accessor.sparse is not None:
                if accessor.sparse.indices is not None and accessor.sparse.indices.bufferView is not None:
                    buffer_view_indices.add(accessor.sparse.indices.bufferView)
                if accessor.sparse.values is not None and accessor.sparse.values.bufferView is not None:
                    buffer_view_indices.add(accessor.sparse.values.bufferView)
        return buffer_view_indices

    def _remove_buffer_views_by_indices(self, indices: Iterable[int]):
        for i in sorted(indices, reverse=True):
            self._remove_buffer_view_by_index(i)

    def _remove_buffer_view_by_index(self, i: int):
        """
        Removes a buffer view from the model by index. Assumes the model has buffer views and the index is valid, and
        that the buffer view is not being referenced by any other parts of the model (i.e., accessors or images).
        When removing multiple buffer view indices, care must be taken to remove the indices in descending order
        (i.e., if removing buffer views with indices [2,3,5], this method should be called first with 5, then with 3,
        then with 2).
        """
        self.model.bufferViews.pop(i)
        for accessor in self.model.accessors or []:
            if accessor.bufferView > i:
                accessor.bufferView -= 1
            if accessor.sparse is not None:
                accessor_indices = accessor.sparse.indices
                if accessor_indices is not None and accessor_indices.bufferView > i:
                    accessor_indices.bufferView -= 1
                accessor_values = accessor.sparse.values
                if accessor_values is not None and accessor_values.bufferView > i:
                    accessor_values.bufferView -= 1
        for image in self.model.images or []:
            if image.bufferView is not None and image.bufferView > i:
                image.bufferView -= 1


def _get_resource(uri, basepath: str, autoload: bool = False) -> Optional[GLTFResource]:
    scheme, netloc, urlpath, params, query, fragment = urlparse(uri)
    if netloc:
        return ExternalResource(uri)
    elif scheme == "data":
        return Base64Resource.from_uri(uri)
    elif not scheme:
        return FileResource(unquote(uri), basepath, autoload)
    return None
