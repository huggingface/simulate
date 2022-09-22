import base64
import json
import os
import tempfile
from os import path
from unittest import TestCase

from simulate.assets.gltflib import (
    GLB_BINARY_CHUNK_TYPE,
    GLTF,
    Accessor,
    Asset,
    Base64Resource,
    Buffer,
    BufferView,
    ExternalResource,
    FileResource,
    GLBResource,
    GLTFModel,
    Image,
    Sparse,
    SparseIndices,
    SparseValues,
)

from ..util import custom_sample, get_file_from_hub, sample


class TestGLTF(TestCase):
    def assert_gltf_files_equal(self, filename1, filename2):
        """Helper method for asserting two GLTF files contain equivalent JSON"""
        with open(filename1, "r") as f1:
            data1 = json.loads(f1.read())
        with open(filename2, "r") as f2:
            data2 = json.loads(f2.read())
        self.assertDictEqual(data1, data2)

    def test_load(self):
        """Basic test ensuring the class can successfully load a minimal GLTF 2.0 file."""
        # Act
        gltf = GLTF.load(custom_sample("Minimal/minimal.gltf"))

        # Assert
        self.assertIsInstance(gltf, GLTF)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), gltf.model)

    def test_export(self):
        """Basic test ensuring the class can successfully save a minimal GLTF 2.0 file."""
        # Arrange
        gltf = GLTF(model=GLTFModel(asset=Asset(version="2.0")))
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "minimal.gltf")

            # Act
            gltf.export(filename)

            # Assert
            self.assertTrue(path.exists(filename))
            self.assert_gltf_files_equal(filename, custom_sample("Minimal/minimal.gltf"))

    def test_export_creates_directories(self):
        """Create directories if necessary when exporting a model to a directory that does not exist"""
        # Arrange
        gltf = GLTF(model=GLTFModel(asset=Asset(version="2.0")))
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "nested", "directory", "minimal.gltf")

            # Act
            gltf.export(filename)

            # Assert
            self.assert_gltf_files_equal(custom_sample("Minimal/minimal.gltf"), filename)

    def test_load_file_resource(self):
        """External files referenced in a glTF model should be loaded as FileResource"""
        # Act
        gltf = GLTF.load(sample("TriangleWithoutIndices"))

        # Assert
        self.assertIsInstance(gltf.resources, list)
        resource = gltf.get_resource("triangleWithoutIndices.bin")
        self.assertIsInstance(resource, FileResource)
        self.assertEqual("triangleWithoutIndices.bin", resource.filename)

    def test_load_file_resource_no_autoload(self):
        """File resource contents should not be autoloaded by default"""
        # Act
        gltf = GLTF.load(sample("TriangleWithoutIndices"))
        resource = gltf.get_resource("triangleWithoutIndices.bin")

        # Assert
        self.assertIsInstance(resource, FileResource)
        self.assertFalse(resource.loaded)
        self.assertIsNone(resource.data)

    def test_load_file_resource_with_autoload(self):
        """When load_file_resources is true, file resource contents should be autoloaded"""
        # Act
        gltf = GLTF.load(sample("TriangleWithoutIndices"), load_file_resources=True)
        resource = gltf.get_resource("triangleWithoutIndices.bin")

        # Assert
        self.assertIsInstance(resource, FileResource)
        self.assertTrue(resource.loaded)
        bin_file = get_file_from_hub("TriangleWithoutIndices", "triangleWithoutIndices.bin", "glTF")
        with open(bin_file, "rb") as f:
            data = f.read()
        self.assertEqual(data, resource.data)

    def test_load_image_resources(self):
        """Ensure image resources are loaded"""
        # Act
        gltf = GLTF.load(sample("BoxTextured"), load_file_resources=True)
        texture = gltf.get_resource("CesiumLogoFlat.png")

        # Assert
        self.assertIsInstance(texture, FileResource)
        bin_file = get_file_from_hub("BoxTextured", "CesiumLogoFlat.png", "glTF")
        with open(bin_file, "rb") as f:
            texture_data = f.read()
        self.assertEqual(texture_data, texture.data)

    def test_load_external_resources(self):
        """External resources should be parsed as ExternalResource instances, but otherwise ignored (for now)"""
        # Act
        gltf = GLTF.load(custom_sample("External/external.gltf"))
        uri = "http://www.example.com/image.jpg"
        resource = gltf.get_resource(uri)

        # Assert
        self.assertIsInstance(resource, ExternalResource)
        self.assertEqual(uri, resource.uri)
        # For now, attempting to access the resource data should throw a ValueError
        with self.assertRaises(ValueError):
            _ = resource.data

    def test_load_provided_resources(self):
        """
        Resources that are passed in to the load method should be used if provided (rather than attempting to load
        these resources from the filesystem).
        """
        # Arrange
        data = b"sample binary data"
        resource = FileResource("triangleWithoutIndices.bin", data=data)

        # Act
        gltf = GLTF.load(sample("TriangleWithoutIndices"), resources=[resource])
        loaded_resource = gltf.get_resource("triangleWithoutIndices.bin")

        # Assert
        self.assertIs(loaded_resource, resource)
        self.assertEqual(data, loaded_resource.data)
        self.assertIsInstance(loaded_resource, FileResource)
        self.assertTrue(loaded_resource.loaded)

    def test_export_file_resources(self):
        """Test exporting a GLTF model with external file resources"""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[resource])
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "sample.gltf")

            # Act
            gltf.export(filename, save_file_resources=True)

            # Assert
            resource_filename = path.join(temp_dir, "buffer.bin")
            self.assertTrue(path.exists(resource_filename))
            with open(resource_filename, "rb") as f:
                self.assertEqual(data, f.read())

    def test_export_file_resources_creates_missing_parent_dirs(self):
        """
        When exporting a GLTF model with external file resources, missing directories should be created automatically.
        """
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("subdir/buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="subdir/buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[resource])
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "sample.gltf")

            # Act
            gltf.export(filename, save_file_resources=True)

            # Assert
            resource_filename = path.join(temp_dir, "subdir", "buffer.bin")
            self.assertTrue(path.exists(resource_filename))
            with open(resource_filename, "rb") as f:
                self.assertEqual(data, f.read())

    def test_skip_exporting_file_resources(self):
        """
        Ensure external file resources are skipped when exporting a GLTF model with save_file_resources set to False
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            resource_filename = path.join(temp_dir, "buffer.bin")
            if path.exists(resource_filename):
                os.remove(resource_filename)
            data = b"sample binary data"
            bytelen = len(data)
            resource = FileResource("buffer.bin", data=data)
            model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
            gltf = GLTF(model=model, resources=[resource])
            filename = path.join(temp_dir, "sample.gltf")

            # Act
            gltf.export(filename, save_file_resources=False)

            # Assert
            self.assertFalse(path.exists(resource_filename))

    # def test_validate_file_resources_in_buffer_when_exporting(self):
    #     """
    #     Test validation for missing external resources referenced in the buffers array when exporting with
    #     save_file_resources set to True
    #     """
    #     # Arrange
    #     model = GLTFModel(asset=Asset(version='2.0'), buffers=[Buffer(uri='buffer.bin', byteLength=1024)])
    #     gltf = GLTF(model=model)
    #     filename = path.join(TEMP_DIR, 'sample.gltf')

    #     # Act/Assert
    #     with self.assertRaisesRegex(RuntimeError, 'Missing resource'):
    #         gltf.export(filename, save_file_resources=True)

    # def test_validate_file_resources_in_image_when_exporting(self):
    #     """
    #     Test validation for missing external resources referenced in the images array when exporting with
    #     save_file_resources set to True
    #     """
    #     # Arrange
    #     model = GLTFModel(asset=Asset(version='2.0'), images=[Image(uri='buffer.bin')])
    #     gltf = GLTF(model=model)
    #     filename = path.join(TEMP_DIR, 'sample.gltf')

    #     # Act/Assert
    #     with self.assertRaisesRegex(RuntimeError, 'Missing resource'):
    #         gltf.export(filename, save_file_resources=True)

    def test_load_glb(self):
        """Ensure a model can be loaded from a binary glTF (GLB) file"""
        # Act
        gltf = GLTF.load(sample("Box", "glTF-Binary"))

        # Assert
        self.assertEqual("2.0", gltf.model.asset.version)
        self.assertIsNone(gltf.model.buffers[0].uri)
        self.assertEqual(648, gltf.model.buffers[0].byteLength)
        self.assertEqual(1, len(gltf.resources))
        self.assertEqual(1, len(gltf.glb_resources))
        resource = gltf.resources[0]
        self.assertIsInstance(resource, GLBResource)
        self.assertEqual(648, len(resource.data))

    def test_clone_no_resources(self):
        """Basic test of the clone method for a GLTF model with no resources."""
        # Arrange
        gltf = GLTF(model=GLTFModel(asset=Asset(version="2.0")))

        # Act
        cloned_gltf = gltf.clone()

        # Assert
        # Original and cloned model should be distinct instances
        self.assertIsNot(gltf, cloned_gltf)
        # Model content should be the same
        self.assertEqual(gltf.model, cloned_gltf.model)

    def test_clone_file_resources(self):
        """Cloning a model with file resources should clone both the model and its associated resources."""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[resource])

        # Act
        cloned_gltf = gltf.clone()

        # Assert
        # Original and cloned model should be distinct instances
        self.assertIsNot(gltf, cloned_gltf)
        # Model content should be the same
        self.assertEqual(gltf.model, cloned_gltf.model)
        # Resource list should be cloned
        self.assertIsNot(gltf.resources, cloned_gltf.resources)
        # Resource list should still contain one FileResource
        self.assertEqual(1, len(cloned_gltf.resources))
        cloned_file_resource = cloned_gltf.resources[0]
        self.assertIsInstance(cloned_file_resource, FileResource)
        # FileResource should be cloned
        self.assertIsNot(cloned_file_resource, resource)
        # Since the original file resource was loaded, the cloned file resource should be loaded as well
        self.assertTrue(cloned_file_resource.loaded)
        # Resource uri and data should be the same
        self.assertEqual(resource.uri, cloned_file_resource.uri)
        self.assertEqual(resource.data, cloned_file_resource.data)

    def test_cloned_file_resources_remains_not_loaded_if_original_was_not_loaded(self):
        """
        When cloning a model with a FileResource that was not explicitly loaded, the cloned FileResource should also
        remain not loaded.
        """
        # Arrange
        # Load a glTF model with load_file_resources set to False
        gltf = GLTF.load(sample("BoxTextured"), load_file_resources=False)
        # Resource should initially not be loaded
        resource = gltf.get_resource("CesiumLogoFlat.png")
        self.assertIsInstance(resource, FileResource)
        self.assertFalse(resource.loaded)

        # Act
        cloned_gltf = gltf.clone()

        # Assert
        # Original and cloned model should be distinct instances
        self.assertIsNot(gltf, cloned_gltf)
        # Model content should be the same
        self.assertEqual(gltf.model, cloned_gltf.model)
        # Resource list should be cloned
        self.assertIsNot(gltf.resources, cloned_gltf.resources)
        # Resource list should contain two FileResources
        self.assertEqual(2, len(cloned_gltf.resources))
        cloned_file_resource = cloned_gltf.get_resource("CesiumLogoFlat.png")
        self.assertIsInstance(cloned_file_resource, FileResource)
        # FileResource should be cloned
        self.assertIsNot(cloned_file_resource, resource)
        # Since the original file resource was not loaded, the cloned file resource should also remain not loaded
        self.assertFalse(cloned_file_resource.loaded)
        # Cloned resource uri should be the same
        self.assertEqual("CesiumLogoFlat.png", cloned_file_resource.uri)
        # Resource data should be None since it was not loaded
        self.assertIsNone(cloned_file_resource.data)

    def test_clone_model_with_glb_resource(self):
        """Cloning a model with a GLB resource should clone both the model and its associated resources."""
        # Arrange
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(byteLength=4)])
        resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[resource])

        # Act
        cloned_gltf = gltf.clone()

        # Assert
        # Resource list should still contain one GLBResource
        self.assertEqual(1, len(cloned_gltf.resources))
        cloned_glb_resource = cloned_gltf.resources[0]
        self.assertIsInstance(cloned_glb_resource, GLBResource)
        # GLBResource should be cloned
        self.assertIsNot(cloned_glb_resource, resource)
        # GLBResource uri should be None
        self.assertIsNone(cloned_glb_resource.uri)
        # Resource data should be the same
        self.assertEqual(resource.data, cloned_glb_resource.data)

    def test_embed_file_resource(self):
        """Test embedding a file resource"""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)],
            bufferViews=[BufferView(buffer=0, byteOffset=0, byteLength=18)],
        )
        file_resource = FileResource(filename="buffer.bin", data=data)
        gltf = GLTF(model=model, resources=[file_resource])

        # Act
        glb_resource = gltf.embed_resource(file_resource)

        # Assert
        # Model should now contain a single GLB resource
        self.assertEqual([glb_resource], gltf.resources)
        # Resource data should be null-padded to a multiple of 4 bytes
        self.assertEqual(b"sample binary data\x00\x00", glb_resource.data)
        # Original file resource should not be mutated
        self.assertEqual(b"sample binary data", file_resource.data)
        # Buffer URI should now be undefined since it is embedded, and byte length should be padded to a multiple of 4
        self.assertEqual([Buffer(byteLength=20)], model.buffers)
        # Buffer view should not be modified in this case
        self.assertEqual([BufferView(buffer=0, byteOffset=0, byteLength=18)], model.bufferViews)

    def test_embed_glb_resource_does_nothing(self):
        """Ensure that calling embed_resource on a GLBResource does nothing (since it is already embedded)"""
        # Arrange
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(byteLength=4)])
        resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[resource])

        # Act
        glb_resource = gltf.embed_resource(resource)

        # Assert
        self.assertIs(glb_resource, resource)
        self.assertEqual([Buffer(byteLength=4)], model.buffers)

    def test_embed_file_resource_with_existing_glb_resources(self):
        """Ensure that embedding a file resource works correctly when the model already has existing GLB resources."""
        # Arrange
        # Existing GLB resource
        glb_resource_data = b"some data"
        glb_resource_bytelen = len(glb_resource_data)
        glb_resource = GLBResource(glb_resource_data)
        # Another GLB resource with a custom resource type
        custom_glb_resource_data = b"more data"
        custom_glb_resource = GLBResource(custom_glb_resource_data, resource_type=123)
        # Sample buffer 1 data (to be embedded)
        buffer_1_filename = "buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample buffer 2 data (to remain external)
        buffer_2_filename = "buffer_2.bin"
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        # Sample image data (to be embedded)
        image_filename = "image.png"
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # File Resources
        file_resource_1 = FileResource(filename=buffer_1_filename, data=buffer_1_data)
        file_resource_2 = FileResource(filename=buffer_2_filename, data=buffer_2_data)
        file_resource_3 = FileResource(filename=image_filename, data=image_data, mimetype="image/jpeg")
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(byteLength=glb_resource_bytelen),
                Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=5),
                BufferView(buffer=0, byteOffset=5, byteLength=4),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
                BufferView(buffer=2, byteOffset=0, byteLength=10),
                BufferView(buffer=2, byteOffset=10, byteLength=12),
            ],
            images=[Image(uri=image_filename)],
        )
        gltf = GLTF(
            model=model,
            resources=[glb_resource, custom_glb_resource, file_resource_1, file_resource_2, file_resource_3],
        )

        # Act
        gltf.embed_resource(file_resource_1)
        gltf.embed_resource(file_resource_3)

        # Assert
        # There should now be 3 resources total (existing GLB resource, the custom GLB resource, and file_resource_2
        # which was not embedded)
        self.assertEqual(3, len(gltf.resources))
        # Ensure the existing GLB resource is still present
        self.assertIs(glb_resource, gltf.get_glb_resource())
        # Existing GLB resource should have its original data together with the data from file_resource_1 and
        # file_resource_3 (each block null-padded to 4 byte intervals).
        self.assertEqual(
            b"some data\x00\x00\x00sample buffer one data\x00\x00sample image data\x00\x00\x00", glb_resource.data
        )
        # The custom GLB resource should still be present and not mutated in any way
        self.assertIs(custom_glb_resource, gltf.get_glb_resource(123))
        self.assertEqual(b"more data", custom_glb_resource.data)
        # file_resource_2 should remain external with its data intact
        self.assertIs(file_resource_2, gltf.get_resource(buffer_2_filename))
        self.assertEqual(b"sample buffer two data", file_resource_2.data)
        # First buffer (referring to the embedded GLB buffer) should be expanded, and its URI should remain undefined
        self.assertIsNone(model.buffers[0].uri)
        self.assertEqual(56, model.buffers[0].byteLength)
        # Second buffer should remain in the model and have its original data intact since it was not embedded
        self.assertEqual(Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen), model.buffers[1])
        # There should be two buffers total
        self.assertEqual(2, len(model.buffers))
        # Ensure buffer view contents match what is expected. The offsets and byte lengths are adjusted to point to the
        # embedded data. There should be a new buffer view for the embedded image
        self.assertEqual(
            [
                BufferView(buffer=0, byteOffset=0, byteLength=5),
                BufferView(buffer=0, byteOffset=5, byteLength=4),
                BufferView(buffer=0, byteOffset=12, byteLength=10),
                BufferView(buffer=0, byteOffset=22, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
                BufferView(buffer=0, byteOffset=36, byteLength=image_bytelen),
            ],
            model.bufferViews,
        )
        # Embedded image should now point to a buffer view instead
        self.assertEqual([Image(uri=None, bufferView=6, mimeType="image/jpeg")], model.images)

    def test_embed_missing_resource_raises_error(self):
        """Attempting to embed a resource that is not present in the resources list should raise a ValueError"""
        # Arrange
        file_resource = FileResource(filename="buffer.bin", data=b"sample binary data")
        gltf = GLTF(model=GLTFModel(asset=Asset(version="2.0")))

        # Act/Assert
        with self.assertRaises(ValueError):
            gltf.embed_resource(file_resource)

    def test_embed_external_resource_raises_error(self):
        """Attempting to embed an ExternalResource should raise a ValueError (not yet supported)"""
        # Arrange
        resource = ExternalResource(uri="http://www.example.com/")
        gltf = GLTF(model=GLTFModel(asset=Asset(version="2.0")), resources=[resource])

        # Act/Assert
        with self.assertRaises(TypeError):
            gltf.embed_resource(resource)

    def test_export_glb(self):
        """Basic test to ensure a model can be saved in GLB format"""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        file_resource = FileResource(filename="buffer.bin", data=data)
        gltf = GLTF(model=model, resources=[file_resource])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "sample.glb")
            gltf2 = gltf.export(filename)

            # Assert
            # Resources on the original model instance should not be mutated
            self.assertEqual([file_resource], gltf.resources)
            self.assertEqual(data, file_resource.data)
            # Exported model should contain a single GLB resource
            self.assertEqual(1, len(gltf2.resources))
            self.assertIsInstance(gltf2.resources[0], GLBResource)
            # Read the exported file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Binary data should be padded to a multiple of 4
            self.assertEqual(20, buffer.byteLength)
            # Original model instance should retain its buffer with the original uri
            self.assertEqual([Buffer(uri="buffer.bin", byteLength=bytelen)], gltf.model.buffers)
            # Ensure embedded GLB resource was parsed correctly
            self.assertEqual(1, len(glb.resources))
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be null-padded so its length is a multiple of 4 bytes
            self.assertEqual(b"sample binary data\x00\x00", resource.data)
            # Original resource data should not be mutated
            self.assertEqual(b"sample binary data", file_resource.data)

    def test_export_glb_multiple_buffers(self):
        """
        Ensures that a model with multiple buffers and buffer views is exported correctly as GLB. The buffers should be
        merged into a single buffer, and all buffer views that reference the buffer should have their byte offsets
        adjusted.
        """
        # Arrange
        data1 = b"sample binary data"
        bytelen1 = len(data1)
        data2 = b"some more binary data"
        bytelen2 = len(data2)
        file_resource_1 = FileResource(filename="buffer1.bin", data=data1)
        file_resource_2 = FileResource(filename="buffer2.bin", data=data2)
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(uri="buffer1.bin", byteLength=bytelen1), Buffer(uri="buffer2.bin", byteLength=bytelen2)],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=8),
                BufferView(buffer=1, byteOffset=0, byteLength=21),
            ],
        )
        gltf = GLTF(model=model, resources=[file_resource_1, file_resource_2])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_multiple_buffers.glb")
            gltf2 = gltf.export(filename)

            # Assert
            # Resources on the original model instance should not be mutated
            self.assertEqual([file_resource_1, file_resource_2], gltf.resources)
            self.assertEqual(data1, file_resource_1.data)
            self.assertEqual(data2, file_resource_2.data)
            # The exported model should contain a single GLB resource
            self.assertEqual(1, len(gltf2.resources))
            self.assertIsInstance(gltf2.resources[0], GLBResource)
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            # The two buffers should be merged into one
            self.assertEqual(1, len(glb.model.buffers))
            # Buffer URI should be undefined since the data is now embedded
            buffer = glb.model.buffers[0]
            self.assertIsNone(buffer.uri)
            # Original model instance should retain its original buffers and buffer views
            self.assertEqual(
                [Buffer(uri="buffer1.bin", byteLength=bytelen1), Buffer(uri="buffer2.bin", byteLength=bytelen2)],
                gltf.model.buffers,
            )
            self.assertEqual(
                [
                    BufferView(buffer=0, byteOffset=0, byteLength=10),
                    BufferView(buffer=0, byteOffset=10, byteLength=8),
                    BufferView(buffer=1, byteOffset=0, byteLength=21),
                ],
                gltf.model.bufferViews,
            )
            # Ensure embedded GLB resource was parsed correctly
            self.assertEqual(1, len(glb.resources))
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(b"sample binary data\x00\x00some more binary data\x00\x00\x00", resource.data)
            self.assertEqual(44, buffer.byteLength)
            # Buffer views should now point to the GLB buffer (index 0) and have their offsets adjusted based on the
            # merged data.
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=10), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=10, byteLength=8), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=0, byteOffset=20, byteLength=21), glb.model.bufferViews[2])

    def test_export_glb_embed_image(self):
        """Tests embedding an image into the GLB that was previously an external file reference"""
        # Arrange
        data = b"sample image data"
        bytelen = len(data)
        image_filename = "image.png"
        model = GLTFModel(asset=Asset(version="2.0"), images=[Image(uri=image_filename)])
        gltf = GLTF(model=model, resources=[FileResource(filename=image_filename, data=data, mimetype="image/jpeg")])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_embed_image.glb")
            gltf.export(filename)

            # Assert
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Binary data should be padded to a multiple of 4
            self.assertEqual(20, buffer.byteLength)
            # Ensure embedded GLB resource was parsed correctly
            self.assertEqual(1, len(glb.resources))
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be null-padded so its length is a multiple of 4 bytes
            self.assertEqual(b"sample image data\x00\x00\x00", resource.data)
            # Ensure image was transformed so it points to a buffer view
            image = glb.model.images[0]
            self.assertIsInstance(image, Image)
            self.assertEqual(0, image.bufferView)
            # Image URI should now be undefined since it is embedded
            self.assertIsNone(image.uri)
            # MIME type is required if image is stored in a buffer. Ensure it got stored correctly based on what we
            # passed in via the FileResource (even if it's not technically the correct MIME type for a PNG image).
            self.assertEqual("image/jpeg", image.mimeType)
            # Ensure that a buffer view was created for the embedded image
            self.assertEqual(1, len(glb.model.bufferViews))
            buffer_view = glb.model.bufferViews[0]
            self.assertIsInstance(buffer_view, BufferView)
            # Ensure buffer view has the correct information
            self.assertEqual(0, buffer_view.buffer)
            self.assertEqual(0, buffer_view.byteOffset)
            self.assertEqual(bytelen, buffer_view.byteLength)

    def test_export_glb_mixed_resources(self):
        """Tests embedding both buffer and image resources into a GLB"""
        # Arrange
        # Sample buffer 1 data
        buffer_1_filename = "buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample buffer 2 data
        buffer_2_filename = "buffer_2.bin"
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        # Sample image data
        image_filename = "image.png"
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # File Resources
        file_resource_1 = FileResource(filename=buffer_1_filename, data=buffer_1_data)
        file_resource_2 = FileResource(filename=buffer_2_filename, data=buffer_2_data)
        file_resource_3 = FileResource(filename=image_filename, data=image_data, mimetype="image/jpeg")
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
            ],
            images=[Image(uri=image_filename)],
        )
        gltf = GLTF(model=model, resources=[file_resource_1, file_resource_2, file_resource_3])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_mixed_resources.glb")
            gltf2 = gltf.export(filename)

            # Assert
            # Resources on the original model instance should not be mutated
            self.assertEqual([file_resource_1, file_resource_2, file_resource_3], gltf.resources)
            self.assertEqual(buffer_1_data, file_resource_1.data)
            self.assertEqual(buffer_2_data, file_resource_2.data)
            self.assertEqual(image_data, file_resource_3.data)
            # The exported model should contain a single GLB resource
            self.assertEqual(1, len(gltf2.resources))
            self.assertIsInstance(gltf2.resources[0], GLBResource)
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Original model instance should retain its original buffers, buffer views, and images
            self.assertEqual(
                [
                    Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                    Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
                ],
                gltf.model.buffers,
            )
            self.assertEqual(
                [
                    BufferView(buffer=0, byteOffset=0, byteLength=10),
                    BufferView(buffer=0, byteOffset=10, byteLength=12),
                    BufferView(buffer=1, byteOffset=0, byteLength=10),
                    BufferView(buffer=1, byteOffset=10, byteLength=12),
                ],
                gltf.model.bufferViews,
            )
            self.assertEqual([Image(uri=image_filename)], gltf.model.images)
            # Ensure embedded GLB resource was parsed correctly
            self.assertEqual(1, len(glb.resources))
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(
                b"sample buffer one data\x00\x00sample buffer two data\x00\x00sample image data\x00\x00\x00",
                resource.data,
            )
            self.assertEqual(68, buffer.byteLength)
            # Buffer views should now point to the GLB buffer (index 0) and have their offsets adjusted based on the
            # merged data.
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=10), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=10, byteLength=12), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=0, byteOffset=24, byteLength=10), glb.model.bufferViews[2])
            self.assertEqual(BufferView(buffer=0, byteOffset=34, byteLength=12), glb.model.bufferViews[3])
            # Ensure a buffer view was added for the embedded image
            self.assertEqual(5, len(glb.model.bufferViews))
            # Ensure the image buffer view has the correct byte length and offset
            image_buffer_view = glb.model.bufferViews[4]
            self.assertIsInstance(image_buffer_view, BufferView)
            self.assertEqual(0, image_buffer_view.buffer)
            self.assertEqual(48, image_buffer_view.byteOffset)
            self.assertEqual(image_bytelen, image_buffer_view.byteLength)
            # Ensure image was transformed so it points to a buffer view
            image = glb.model.images[0]
            self.assertIsInstance(image, Image)
            self.assertEqual(4, image.bufferView)
            # Image URI should now be undefined since it is embedded
            self.assertIsNone(image.uri)

    def test_export_glb_with_embedded_image(self):
        """
        Tests exporting a model to GLB that already contains an embedded image, and a FileResource to be newly embedded.
        """
        # Arrange
        # Sample buffer 1 data (to be embedded)
        buffer_1_filename = "buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample image data (already embedded)
        image_filename = "image.png"
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # Create resources
        glb_resource = GLBResource(data=image_data)
        file_resource = FileResource(filename=buffer_1_filename, data=buffer_1_data)
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(byteLength=image_bytelen), Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen)],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
                BufferView(buffer=1, byteOffset=0, byteLength=buffer_1_bytelen),
            ],
            images=[Image(uri=image_filename, bufferView=0)],
        )
        gltf = GLTF(model=model, resources=[glb_resource, file_resource])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_with_embedded_image.glb")
            gltf2 = gltf.export(filename)

            # Assert
            # Resources on the original model instance should not be mutated
            self.assertEqual([glb_resource, file_resource], gltf.resources)
            self.assertEqual(b"sample image data", glb_resource.data)
            self.assertEqual(b"sample buffer one data", file_resource.data)
            # The exported model should contain a single GLB resource
            self.assertEqual(1, len(gltf2.resources))
            self.assertIsInstance(gltf2.resources[0], GLBResource)
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Original model instance should retain its original buffers, buffer views, and images
            self.assertEqual(
                [Buffer(byteLength=image_bytelen), Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen)],
                gltf.model.buffers,
            )
            self.assertEqual(
                [
                    BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
                    BufferView(buffer=1, byteOffset=0, byteLength=buffer_1_bytelen),
                ],
                gltf.model.bufferViews,
            )
            self.assertEqual([Image(uri=image_filename, bufferView=0)], gltf.model.images)
            # Ensure embedded GLB resource was parsed correctly
            self.assertEqual(1, len(glb.resources))
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(b"sample image data\x00\x00\x00sample buffer one data\x00\x00", resource.data)
            self.assertEqual(44, buffer.byteLength)
            # Buffer views should now point to the GLB buffer (index 0) and have their offsets adjusted based on the
            # merged data.
            self.assertEqual(2, len(glb.model.bufferViews))
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=17), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=20, byteLength=22), glb.model.bufferViews[1])

    def test_export_glb_with_existing_glb_buffer_and_resource(self):
        """
        Ensure that when exporting a GLB model with an existing GLBResource and a GLB buffer works correctly (existing
        buffer and resource should be preserved, and no new ones added)
        """
        # Arrange
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(byteLength=4)])
        resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[resource])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_with_existing_glb_buffer_and_resource.glb")
            gltf.export(filename)

            # Assert
            # Load back the GLB and ensure it has the correct structure
            glb = GLTF.load(filename)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            self.assertIsNone(buffer.uri)
            self.assertEqual(4, buffer.byteLength)
            # Validate GLB resource remains as is
            self.assertEqual(1, len(glb.resources))
            glb_resource = glb.get_glb_resource()
            self.assertIsInstance(glb_resource, GLBResource)
            self.assertEqual(b"data", glb_resource.data)

    def test_export_glb_with_external_image_resource(self):
        """
        Tests exporting a binary GLB file with image resources remaining external.
        """
        # Arrange
        # Sample buffer 1 data
        buffer_1_filename = "buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample buffer 2 data
        buffer_2_filename = "buffer_2.bin"
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        # Sample image data (this will remain external)
        image_filename = "sample_image.png"
        image_data = b"sample image data"
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
            ],
            images=[Image(uri=image_filename)],
        )
        gltf = GLTF(
            model=model,
            resources=[
                FileResource(filename=buffer_1_filename, data=buffer_1_data),
                FileResource(filename=buffer_2_filename, data=buffer_2_data),
                FileResource(filename=image_filename, data=image_data, mimetype="image/jpeg"),
            ],
        )

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the GLB (do not embed image resources)
            filename = path.join(temp_dir, "test_export_glb_with_external_image_resource.glb")
            gltf.export_glb(filename, embed_image_resources=False)

            # Assert
            # Ensure the image got saved
            self.assertTrue(path.exists(path.join(temp_dir, image_filename)))
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename, load_file_resources=True)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Ensure there are two resources since the image should remain external
            self.assertEqual(2, len(glb.resources))
            # Ensure embedded GLB resource was parsed correctly
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(b"sample buffer one data\x00\x00sample buffer two data\x00\x00", resource.data)
            self.assertEqual(48, buffer.byteLength)
            # Buffer views should now point to the GLB buffer (index 0) and have their offsets adjusted based on the
            # merged data.
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=10), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=10, byteLength=12), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=0, byteOffset=24, byteLength=10), glb.model.bufferViews[2])
            self.assertEqual(BufferView(buffer=0, byteOffset=34, byteLength=12), glb.model.bufferViews[3])
            # Ensure there are still 4 buffer views (rather than 5 if the image was embedded)
            self.assertEqual(4, len(glb.model.bufferViews))
            # Ensure the image resource remains external
            image_resource = glb.get_resource(image_filename)
            self.assertIsInstance(image_resource, FileResource)
            # Ensure image filename and data are retained after export
            self.assertEqual(image_filename, image_resource.filename)
            self.assertEqual(b"sample image data", image_resource.data)
            # Ensure image is retained in the model structure
            image = glb.model.images[0]
            self.assertIsInstance(image, Image)
            self.assertEqual(image_filename, image.uri)

    def test_export_glb_with_more_than_two_resources(self):
        """
        When exporting a binary GLB file with more than two binary data resources, ensure that all resources are
        embedded correctly. In particular, since we are adding a GLB buffer while also removing buffers that used to be
        external files, ensure that no buffers are missed as we are iterating the buffers collection (which is being
        modified during iteration).
        """
        # Arrange
        # Sample buffer 1 data
        buffer_1_filename = "buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample buffer 2 data
        buffer_2_filename = "buffer_2.bin"
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        # Sample buffer 3 data
        buffer_3_filename = "buffer_3.bin"
        buffer_3_data = b"sample buffer three data"
        buffer_3_bytelen = len(buffer_3_data)
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
                Buffer(uri=buffer_3_filename, byteLength=buffer_3_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
                BufferView(buffer=2, byteOffset=0, byteLength=10),
                BufferView(buffer=2, byteOffset=10, byteLength=14),
            ],
        )
        gltf = GLTF(
            model=model,
            resources=[
                FileResource(filename=buffer_1_filename, data=buffer_1_data),
                FileResource(filename=buffer_2_filename, data=buffer_2_data),
                FileResource(filename=buffer_3_filename, data=buffer_3_data),
            ],
        )

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the GLB
            filename = path.join(temp_dir, "test_export_glb_with_more_than_two_resources.glb")
            gltf.export_glb(filename)

            # Assert
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Ensure there is a single GLB resource
            self.assertEqual(1, len(glb.resources))
            glb_resource = glb.get_glb_resource()
            self.assertIsInstance(glb_resource, GLBResource)
            self.assertEqual(glb_resource, glb.resources[0])
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(
                b"sample buffer one data\x00\x00sample buffer two data\x00\x00sample buffer three data",
                glb_resource.data,
            )
            self.assertEqual(72, buffer.byteLength)
            # Buffer views should now point to the GLB buffer (index 0) and have their offsets adjusted based on the
            # merged data.
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=10), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=10, byteLength=12), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=0, byteOffset=24, byteLength=10), glb.model.bufferViews[2])
            self.assertEqual(BufferView(buffer=0, byteOffset=34, byteLength=12), glb.model.bufferViews[3])
            self.assertEqual(BufferView(buffer=0, byteOffset=48, byteLength=10), glb.model.bufferViews[4])
            self.assertEqual(BufferView(buffer=0, byteOffset=58, byteLength=14), glb.model.bufferViews[5])

    def test_export_glb_with_more_than_two_images(self):
        """
        When exporting a binary GLB file with more than two image resources, ensure that all resources are embedded
        correctly.
        """
        # Arrange
        # Sample image 1
        image_1_filename = "sample_image_1.png"
        image_1_data = b"sample image 1 data"
        # Sample image 2
        image_2_filename = "sample_image_2.png"
        image_2_data = b"sample image 2 data"
        # Sample image 3
        image_3_filename = "sample_image_3.png"
        image_3_data = b"sample image 3 data"
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            images=[Image(uri=image_1_filename), Image(uri=image_2_filename), Image(uri=image_3_filename)],
        )
        gltf = GLTF(
            model=model,
            resources=[
                FileResource(filename=image_1_filename, data=image_1_data, mimetype="image/jpeg"),
                FileResource(filename=image_2_filename, data=image_2_data, mimetype="image/jpeg"),
                FileResource(filename=image_3_filename, data=image_3_data, mimetype="image/jpeg"),
            ],
        )

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the GLB
            filename = path.join(temp_dir, "test_export_glb_with_more_than_two_images.glb")
            gltf.export_glb(filename)

            # Assert
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename, load_file_resources=True)
            self.assertEqual(model.asset, glb.model.asset)
            self.assertEqual(1, len(glb.model.buffers))
            buffer = glb.model.buffers[0]
            self.assertIsInstance(buffer, Buffer)
            # Buffer URI should be undefined since the data is now embedded
            self.assertIsNone(buffer.uri)
            # Ensure there is only 1 resource since all images should now be embedded
            self.assertEqual(1, len(glb.resources))
            glb_resource = glb.get_glb_resource()
            self.assertIsInstance(glb_resource, GLBResource)
            self.assertEqual(glb_resource, glb.resources[0])
            # Binary data should be merged and its individual chunks null-padded so that they align to a 4-byte boundary
            self.assertEqual(
                b"sample image 1 data\x00sample image 2 data\x00sample image 3 data\x00", glb_resource.data
            )
            self.assertEqual(60, buffer.byteLength)
            # Buffer views should be created for each image
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=19), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=20, byteLength=19), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=0, byteOffset=40, byteLength=19), glb.model.bufferViews[2])
            self.assertEqual(3, len(glb.model.bufferViews))
            # Ensure images point to correct buffer views
            self.assertEqual(0, glb.model.images[0].bufferView)
            self.assertEqual(1, glb.model.images[1].bufferView)
            self.assertEqual(2, glb.model.images[2].bufferView)
            # Ensure image URIs are undefined since they are now embedded
            self.assertIsNone(glb.model.images[0].uri)
            self.assertIsNone(glb.model.images[1].uri)
            self.assertIsNone(glb.model.images[2].uri)

    def test_export_glb_with_all_resources_remaining_external(self):
        """
        Tests exporting a binary GLB file with all resources (buffer and image) remaining external.
        """
        # Arrange
        # Sample buffer 1 data (this will remain external)
        buffer_1_filename = "sample_8_buffer_1.bin"
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        # Sample buffer 2 data (this will remain external)
        buffer_2_filename = "sample_8_buffer_2.bin"
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        # Sample image data (this will remain external)
        image_filename = "sample_8_image.png"
        image_data = b"sample image data"
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=buffer_1_filename, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_filename, byteLength=buffer_2_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
            ],
            images=[Image(uri=image_filename)],
        )
        gltf = GLTF(
            model=model,
            resources=[
                FileResource(filename=buffer_1_filename, data=buffer_1_data),
                FileResource(filename=buffer_2_filename, data=buffer_2_data),
                FileResource(filename=image_filename, data=image_data, mimetype="image/jpeg"),
            ],
        )

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the GLB (do not embed buffer or image resources)
            filename = path.join(temp_dir, "test_export_glb_with_all_resources_remaining_external.glb")
            gltf.export_glb(filename, embed_buffer_resources=False, embed_image_resources=False)

            # Assert
            # Ensure the buffer and image files got saved
            self.assertTrue(path.exists(path.join(temp_dir, buffer_1_filename)))
            self.assertTrue(path.exists(path.join(temp_dir, buffer_2_filename)))
            self.assertTrue(path.exists(path.join(temp_dir, image_filename)))
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename, load_file_resources=True)
            self.assertEqual(model.asset, glb.model.asset)
            # Ensure there are still 2 buffers (they should not get merged)
            self.assertEqual(2, len(glb.model.buffers))
            buffer1 = glb.model.buffers[0]
            self.assertIsInstance(buffer1, Buffer)
            buffer2 = glb.model.buffers[1]
            self.assertIsInstance(buffer2, Buffer)
            # Ensure buffer URIs and byte lengths are retained
            self.assertEqual(buffer_1_filename, buffer1.uri)
            self.assertEqual(buffer_1_bytelen, buffer1.byteLength)
            self.assertEqual(buffer_2_filename, buffer2.uri)
            self.assertEqual(buffer_2_bytelen, buffer2.byteLength)
            # Ensure there are three resources since all resources should remain external
            self.assertEqual(3, len(glb.resources))
            # Ensure there is no embedded GLB resource
            self.assertIsNone(glb.get_glb_resource())
            # Ensure buffer views are retained with their original byte offsets and byte lengths
            self.assertEqual(BufferView(buffer=0, byteOffset=0, byteLength=10), glb.model.bufferViews[0])
            self.assertEqual(BufferView(buffer=0, byteOffset=10, byteLength=12), glb.model.bufferViews[1])
            self.assertEqual(BufferView(buffer=1, byteOffset=0, byteLength=10), glb.model.bufferViews[2])
            self.assertEqual(BufferView(buffer=1, byteOffset=10, byteLength=12), glb.model.bufferViews[3])
            # Ensure there are still 4 buffer views (rather than 5 if the image was embedded)
            self.assertEqual(4, len(glb.model.bufferViews))
            # Ensure the buffer resources are parsed correctly and can be referenced by URI
            buffer_1_resource = glb.get_resource(buffer_1_filename)
            self.assertIsInstance(buffer_1_resource, FileResource)
            self.assertEqual(buffer_1_filename, buffer_1_resource.filename)
            buffer_2_resource = glb.get_resource(buffer_2_filename)
            self.assertIsInstance(buffer_2_resource, FileResource)
            self.assertEqual(buffer_2_filename, buffer_2_resource.filename)
            # Ensure the image resource remains external
            image_resource = glb.get_resource(image_filename)
            self.assertIsInstance(image_resource, FileResource)
            # Ensure image filename and data are retained after export
            self.assertEqual(image_filename, image_resource.filename)
            self.assertEqual(b"sample image data", image_resource.data)
            # Ensure image is retained in the model structure
            image = glb.model.images[0]
            self.assertIsInstance(image, Image)
            self.assertEqual(image_filename, image.uri)

    def test_export_glb_with_external_image_resource_skip_saving_files(self):
        """
        When exporting a binary GLB with some resources remaining external, test that we can skip actually saving these
        external resources by setting the save_file_resources to False during export.
        """
        # Arrange
        # Sample buffer data
        buffer_filename = "buffer.bin"
        buffer_data = b"sample buffer one data"
        buffer_bytelen = len(buffer_data)
        # Sample image data (this will remain external, and we will skip actually saving it)
        image_filename = "sample_image.png"
        image_data = b"sample image data"
        # Delete sample image if it exists
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = path.join(temp_dir, image_filename)
            if path.exists(image_path):
                os.remove(image_path)
            # Create GLTF Model
            model = GLTFModel(
                asset=Asset(version="2.0"),
                buffers=[Buffer(uri=buffer_filename, byteLength=buffer_bytelen)],
                bufferViews=[BufferView(buffer=0, byteOffset=0, byteLength=22)],
                images=[Image(uri=image_filename)],
            )
            gltf = GLTF(
                model=model,
                resources=[
                    FileResource(filename=buffer_filename, data=buffer_data),
                    FileResource(filename=image_filename, data=image_data, mimetype="image/jpeg"),
                ],
            )

            # Act
            # Export the GLB (do not embed image resources, and skip saving file resources)
            filename = path.join(temp_dir, "test_export_glb_with_external_image_resource_skip_saving_files.glb")
            gltf.export_glb(filename, embed_image_resources=False, save_file_resources=False)

            # Assert
            # Ensure the image did NOT get saved
            self.assertFalse(path.exists(path.join(temp_dir, image_filename)))
            # Read the file back in and verify expected structure
            glb = GLTF.load_glb(filename)
            self.assertEqual(model.asset, glb.model.asset)
            # Ensure there are two resources since the image should remain external
            self.assertEqual(2, len(glb.resources))
            # Ensure embedded GLB resource was parsed correctly
            resource = glb.get_glb_resource()
            self.assertIsInstance(resource, GLBResource)
            # Ensure the image resource remains external
            image_resource = glb.get_resource(image_filename)
            self.assertIsInstance(image_resource, FileResource)
            # Ensure image is retained in the model structure
            image = glb.model.images[0]
            self.assertIsInstance(image, Image)
            self.assertEqual(image_filename, image.uri)
            # Ensure image filename is retained after export
            self.assertEqual(image_filename, image_resource.filename)
            # Loading the resource should raise FileNotFoundError since the image was not actually saved
            with self.assertRaises(FileNotFoundError):
                _ = image_resource.load()

    def test_export_glb_with_resource_not_yet_loaded(self):
        """
        Embedding resources should work when converting a glTF with external file resources that were not explicitly
        loaded when calling GLTF.load(). (This implies the resource will need to be implicitly loaded.)
        """
        # Arrange
        # Load a glTF model with load_file_resources set to False
        gltf = GLTF.load(sample("BoxTextured"), load_file_resources=False)
        # Ensure resource is initially not loaded
        resource = gltf.get_resource("CesiumLogoFlat.png")
        self.assertIsInstance(resource, FileResource)
        self.assertFalse(resource.loaded)

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert the glTF to a GLB
            filename = path.join(temp_dir, "test_export_glb_with_resource_not_yet_loaded.glb")
            exported_glb = gltf.export(filename)

            # Assert
            # Extract the image data from the exported GLB
            glb_resource = exported_glb.get_glb_resource()
            image = exported_glb.model.images[0]
            image_buffer_view = exported_glb.model.bufferViews[image.bufferView]
            offset = image_buffer_view.byteOffset
            bytelen = image_buffer_view.byteLength
            extracted_image_data = glb_resource.data[offset : (offset + bytelen)]
            # Ensure image data matches
            resource.load()
            self.assertEqual(resource.data, extracted_image_data)
            # MIME type should be automatically determined when loading the image
            self.assertEqual("image/png", image.mimeType)
            # Image URI should be undefined since it is now embedded
            self.assertIsNone(image.uri)

    def test_export_glb_with_resource_not_yet_loaded_without_embedding(self):
        """
        When converting a glTF with external file resources that were not explicitly loaded when calling GLTF.load(),
        then converting the glTF to a GLB with the image resource remaining external, it should be loaded and copied
        when calling export_glb.
        """
        # Arrange
        # Load a glTF model with load_file_resources set to False
        gltf = GLTF.load(sample("BoxTextured"), load_file_resources=False)
        # Resource should initially not be loaded
        resource = gltf.get_resource("CesiumLogoFlat.png")
        self.assertIsInstance(resource, FileResource)
        self.assertFalse(resource.loaded)

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert the glTF to a GLB without embedding the resource. However, set save_file_resources to True, so
            # the image should still get loaded and saved.
            filename = path.join(temp_dir, "test_export_glb_with_resource_not_yet_loaded_without_embedding.glb")
            exported_glb = gltf.export_glb(filename, embed_image_resources=False, save_file_resources=True)

            # Assert
            # Original image resource should not be loaded
            self.assertFalse(resource.loaded)
            # Exported image resource should be loaded
            exported_resource = exported_glb.get_resource("CesiumLogoFlat.png")
            self.assertIsInstance(exported_resource, FileResource)
            self.assertTrue(exported_resource.loaded)
            # Ensure image got saved
            image_filename = path.join(temp_dir, "CesiumLogoFlat.png")
            self.assertTrue(path.exists(image_filename))

            bin_file = get_file_from_hub("BoxTextured", "CesiumLogoFlat.png", "glTF")
            with open(bin_file, "rb") as f:
                original_texture_data = f.read()
            with open(image_filename, "rb") as f:
                texture_data = f.read()
            self.assertEqual(original_texture_data, texture_data)

    def test_resource_remains_not_loaded_when_exporting_glb_without_embedding_or_saving_file_resources(self):
        """
        When converting a glTF with external file resources that were not explicitly loaded when calling GLTF.load(),
        the resources should remain not loaded if exporting without embedding or saving image resources.
        """
        # Arrange
        # Load a glTF model with load_file_resources set to False
        gltf = GLTF.load(sample("BoxTextured"), load_file_resources=False)
        # Resource should initially not be loaded
        resource = gltf.get_resource("CesiumLogoFlat.png")
        self.assertIsInstance(resource, FileResource)
        self.assertFalse(resource.loaded)

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert the glTF to a GLB without embedding or saving image resources
            filename = path.join(
                temp_dir,
                "test_resource_remains_not_loaded_when_exporting_glb_without_embedding_or_"
                "saving_file_resources.glb",
            )
            gltf.export_glb(filename, embed_image_resources=False, save_file_resources=False)

            # Assert
            # Ensure resource remains not loaded
            self.assertFalse(resource.loaded)

    def test_export_gltf_raises_error_if_glb_resource_is_present(self):
        """
        When exporting a model as glTF, it may not have a GLB resource (the GLB resource needs to be converted to either
        a FileResource or EmbeddedResource first).
        """
        # Arrange
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(byteLength=4)])
        resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[resource])

        # Act/Assert
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_gltf_raises_error_if_glb_resource_is_present.gltf")
            with self.assertRaises(TypeError):
                gltf.export(filename)

    def test_export_glb_with_multiple_glb_resources(self):
        """Test exporting a GLB with multiple GLB resources with different types."""
        # Arrange
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(byteLength=4)])
        glb_resource_1 = GLBResource(b"data")
        glb_resource_2 = GLBResource(b"more data", resource_type=123)
        gltf = GLTF(model=model, resources=[glb_resource_1, glb_resource_2])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_glb_with_multiple_glb_resources.glb")
            gltf2 = gltf.export(filename)

            # Assert
            # Exported model should have two GLB resources
            self.assertEqual(2, len(gltf2.resources))
            exported_glb_resource_1 = gltf2.resources[0]
            exported_glb_resource_2 = gltf2.resources[1]
            self.assertIsInstance(exported_glb_resource_1, GLBResource)
            self.assertIsInstance(exported_glb_resource_2, GLBResource)
            # Chunk types of both resources should be retained
            self.assertEqual(GLB_BINARY_CHUNK_TYPE, exported_glb_resource_1.resource_type)
            self.assertEqual(123, exported_glb_resource_2.resource_type)

    def test_load_glb_with_multiple_glb_resources(self):
        """Test loading a GLB with multiple GLB resources with different types."""
        # Act
        gltf = GLTF.load(custom_sample("MultipleChunks/MultipleChunks.glb"))

        # Assert
        # Model should have two GLB resources
        self.assertEqual(2, len(gltf.resources))
        self.assertEqual(2, len(gltf.glb_resources))
        self.assertEqual(gltf.resources, gltf.glb_resources)
        # Extract the resources and ensure they are the correct type
        glb_resource_1 = gltf.resources[0]
        glb_resource_2 = gltf.resources[1]
        self.assertIsInstance(glb_resource_1, GLBResource)
        self.assertIsInstance(glb_resource_2, GLBResource)
        # Validate chunk types
        self.assertEqual(GLB_BINARY_CHUNK_TYPE, glb_resource_1.resource_type)
        self.assertEqual(123, glb_resource_2.resource_type)
        # Validate chunk data
        self.assertEqual(b"data", glb_resource_1.data)
        self.assertEqual(b"more data\x00\x00\x00", glb_resource_2.data)

    def test_create_base64_resource_from_uri(self):
        """Ensures a Base64Resource is created successfully using the Base64Resource.from_uri factory method."""
        # Arrage
        uri = "data:application/octet-stream;base64,c2FtcGxlIGJpbmFyeSBkYXRh"

        # Act
        resource = Base64Resource.from_uri(uri)

        # Assert
        self.assertEqual(b"sample binary data", resource.data)
        self.assertEqual("application/octet-stream", resource.mime_type)

    def test_load_gltf_with_base64_resource(self):
        """Basic test to ensure a model with an embedded base64-encoded resource is parsed correctly."""
        # Act
        gltf = GLTF.load(sample("Box", "glTF-Embedded"))

        # Assert
        # Ensure the resource got parsed correctly as a Base64Resource
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIsInstance(resource, Base64Resource)
        # Ensure byte length is correct
        self.assertEqual(648, len(resource.data))

        # Ensure binary data matches
        bin_file = get_file_from_hub("Box", "Box0.bin", "glTF")
        with open(bin_file, "rb") as f:
            data = f.read()
        self.assertEqual(data, resource.data)
        # Ensure buffer URI is preserved as base64
        buffer = gltf.model.buffers[0]
        self.assertTrue(buffer.uri.startswith("data:application/octet-stream;base64,AAAAAAAAAAAAAIA"))
        # Ensure MIME type is parsed correctly
        self.assertEqual("application/octet-stream", resource.mime_type)

    def test_load_gltf_with_base64_image_resource(self):
        """Ensure a base64-encoded image resource is parsed correctly."""
        # Act
        gltf = GLTF.load(sample("BoxTextured", "glTF-Embedded"))

        # Assert
        # There should be two resources (one for the image and another for the buffer data)
        self.assertEqual(2, len(gltf.resources))
        buffer_resource = next(
            r for r in gltf.resources if isinstance(r, Base64Resource) and r.mime_type == "application/octet-stream"
        )
        image_resource = next(
            r for r in gltf.resources if isinstance(r, Base64Resource) and r.mime_type == "image/png"
        )
        # Ensure byte length is correct on both resources
        self.assertEqual(4333, len(image_resource.data))
        self.assertEqual(840, len(buffer_resource.data))

        # Ensure binary data matches on both resources
        bin_file = get_file_from_hub("BoxTextured", "CesiumLogoFlat.png", "glTF")
        with open(bin_file, "rb") as f1:
            image_data = f1.read()
        bin_file = get_file_from_hub("BoxTextured", "BoxTextured0.bin", "glTF")
        with open(bin_file, "rb") as f2:
            buffer_data = f2.read()
        self.assertEqual(image_data, image_resource.data)
        self.assertEqual(buffer_data, buffer_resource.data)
        # Ensure image URI is preserved as base64
        image = gltf.model.images[0]
        self.assertTrue(image.uri.startswith("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA"))
        # Ensure buffer URI is preserved as base64
        buffer = gltf.model.buffers[0]
        self.assertTrue(buffer.uri.startswith("data:application/octet-stream;base64,AAAAAAAAAAAAAIA"))
        # Ensure MIME types are parsed correctly
        self.assertEqual("image/png", image_resource.mime_type)
        self.assertEqual("application/octet-stream", buffer_resource.mime_type)

    def test_export_gltf_with_base64_resources(self):
        """Ensure a model with Base64-encoded resources can be exported successfully"""
        # Arrange
        # Sample buffer 1 data
        buffer_1_data = b"sample buffer one data"
        buffer_1_bytelen = len(buffer_1_data)
        buffer_1_uri = "data:application/octet-stream;base64," + base64.b64encode(buffer_1_data).decode("utf-8")
        # Sample buffer 2 data
        buffer_2_data = b"sample buffer two data"
        buffer_2_bytelen = len(buffer_2_data)
        buffer_2_uri = "data:application/octet-stream;base64," + base64.b64encode(buffer_2_data).decode("utf-8")
        # Sample image data
        image_data = b"sample image data"
        image_uri = "data:image/png;base64," + base64.b64encode(image_data).decode("utf-8")
        # Create resources
        resource_1 = Base64Resource.from_uri(buffer_1_uri)
        resource_2 = Base64Resource.from_uri(buffer_2_uri)
        resource_3 = Base64Resource.from_uri(image_uri)
        # Create GLTF Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=buffer_1_uri, byteLength=buffer_1_bytelen),
                Buffer(uri=buffer_2_uri, byteLength=buffer_2_bytelen),
            ],
            bufferViews=[
                BufferView(buffer=0, byteOffset=0, byteLength=10),
                BufferView(buffer=0, byteOffset=10, byteLength=12),
                BufferView(buffer=1, byteOffset=0, byteLength=10),
                BufferView(buffer=1, byteOffset=10, byteLength=12),
            ],
            images=[Image(uri=image_uri)],
        )
        gltf = GLTF(model=model, resources=[resource_1, resource_2, resource_3])

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_gltf_with_base64_resources.gltf")
            _ = gltf.export(filename)

            # Assert
            # Read the model back in
            loaded_gltf = GLTF.load(filename)
            # Ensure resources got parsed correctly
            self.assertEqual(3, len(loaded_gltf.resources))
            self.assertTrue(buffer_1_uri in [r.uri for r in loaded_gltf.resources])
            self.assertTrue(buffer_2_uri in [r.uri for r in loaded_gltf.resources])
            self.assertTrue(image_uri in [r.uri for r in loaded_gltf.resources])
            # Extract the resources that correspond to the originals (which may have been loaded in different order)
            loaded_resource_1 = next(r for r in loaded_gltf.resources if r.uri == buffer_1_uri)
            loaded_resource_2 = next(r for r in loaded_gltf.resources if r.uri == buffer_2_uri)
            loaded_resource_3 = next(r for r in loaded_gltf.resources if r.uri == image_uri)
            # Ensure all resources got correctly parsed as Base64Resource
            self.assertIsInstance(loaded_resource_1, Base64Resource)
            self.assertIsInstance(loaded_resource_2, Base64Resource)
            self.assertIsInstance(loaded_resource_3, Base64Resource)
            # Ensure data URIs match
            self.assertEqual(buffer_1_uri, loaded_resource_1.uri)
            self.assertEqual(buffer_2_uri, loaded_resource_2.uri)
            self.assertEqual(image_uri, loaded_resource_3.uri)
            # Ensure contents are binary equal
            self.assertEqual(buffer_1_data, loaded_resource_1.data)
            self.assertEqual(buffer_2_data, loaded_resource_2.data)
            self.assertEqual(image_data, loaded_resource_3.data)
            # Ensure MIME types were stored correctly
            self.assertEqual("application/octet-stream", loaded_resource_1.mime_type)
            self.assertEqual("application/octet-stream", loaded_resource_2.mime_type)
            self.assertEqual("image/png", loaded_resource_3.mime_type)
            # Ensure exported GLTF instance contains the same 3 resources
            # self.assertEqual(3, len(exported_gltf.resources))
            # exported_resource_1 = exported_gltf.resources[0]
            # exported_resource_2 = exported_gltf.resources[1]
            # exported_resource_3 = exported_gltf.resources[2]
            # self.assertIsInstance(exported_resource_1, Base64Resource)
            # self.assertIsInstance(exported_resource_2, Base64Resource)
            # self.assertIsInstance(exported_resource_3, Base64Resource)
            # # Ensure resource data in the exported GLTF instance matches
            # self.assertEqual(buffer_1_data, exported_resource_1.data)
            # self.assertEqual(buffer_2_data, exported_resource_2.data)
            # self.assertEqual(image_data, exported_resource_3.data)

    def test_embed_base64_resource_to_glb(self):
        """Ensure base64-encoded resources can be embedded as GLB using embed_resource."""
        # Arrage
        gltf = GLTF.load(sample("BoxTextured", "glTF-Embedded"))
        image_resource = gltf.resources[0]
        buffer_resource = gltf.resources[1]

        # Act
        gltf.embed_resource(image_resource)
        gltf.embed_resource(buffer_resource)

        # Assert
        # There should now be one GLB resource
        self.assertEqual(1, len(gltf.resources))
        glb_resource = gltf.get_glb_resource()
        self.assertIsInstance(glb_resource, GLBResource)
        # Ensure byte length is correct on the resource
        self.assertEqual(5176, len(glb_resource.data))
        # Ensure URIs are now undefined in the model so the data is not being represented twice
        self.assertIsNone(gltf.model.images[0].uri)
        self.assertIsNone(gltf.model.buffers[0].uri)
        # Ensure image MIME type is preserved
        self.assertEqual("image/png", gltf.model.images[0].mimeType)

    def test_export_base64_resource_to_glb(self):
        """Ensure exporting a model containing base64-encoded resources to GLB."""
        # Arrage
        gltf = GLTF.load(sample("BoxTextured", "glTF-Embedded"))

        # Act
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = path.join(temp_dir, "test_export_base64_resource_to_glb.glb")
            exported_glb = gltf.export(filename)

            # Assert
            # Exported GLB instance should contain one GLB resource
            self.assertEqual(1, len(exported_glb.resources))
            exported_glb_resource = exported_glb.get_glb_resource()
            self.assertIsInstance(exported_glb_resource, GLBResource)
            # Ensure byte length is correct on the exported resource
            self.assertEqual(5176, len(exported_glb_resource.data))
            # Read the exported model back in and verify expected structure
            loaded_glb = GLTF.load(filename)
            self.assertEqual(1, len(loaded_glb.resources))
            glb_resource = loaded_glb.get_glb_resource()
            self.assertIsInstance(glb_resource, GLBResource)
            # Ensure byte length is correct on the loaded GLB resource
            self.assertEqual(5176, len(glb_resource.data))
            # Ensure image buffer view points to the embedded GLB buffer and URI is not defined
            buffer_view = loaded_glb.model.images[0].bufferView
            self.assertEqual(0, loaded_glb.model.bufferViews[buffer_view].buffer)
            self.assertIsNone(loaded_glb.model.images[0].uri)
            # Ensure image data matches
            image_resource = next(
                r for r in gltf.resources if isinstance(r, Base64Resource) and r.mime_type == "image/png"
            )
            image_buffer_view_index = loaded_glb.model.images[0].bufferView
            image_buffer_view = loaded_glb.model.bufferViews[image_buffer_view_index]
            offset = image_buffer_view.byteOffset
            bytelen = image_buffer_view.byteLength
            image_data = glb_resource.data[offset : (offset + bytelen)]
            self.assertEqual(image_resource.data, image_data)
            self.assertEqual("image/png", image_resource.mime_type)

    def test_load_gltf_with_external_resource(self):
        """Test that a GLTF with external web URL resources is parsed correctly"""
        # Arrange
        image_uri = "http://www.example.com/image.jpg"
        data_uri = "http://www.example.com/data.bin"

        # Act
        gltf = GLTF.load(custom_sample("External/external.gltf"))

        # Assert
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(image_uri in [r.uri for r in gltf.resources])
        self.assertTrue(data_uri in [r.uri for r in gltf.resources])
        image_resource = next(r for r in gltf.resources if r.uri == image_uri)
        data_resource = next(r for r in gltf.resources if r.uri == data_uri)
        self.assertIsInstance(image_resource, ExternalResource)
        self.assertIsInstance(data_resource, ExternalResource)

    def test_load_glb_with_external_resource(self):
        """Test that a GLB with external web URL resources is parsed correctly"""
        # Arrange
        external_uri = "http://www.example.com/data.bin"

        # Act
        gltf = GLTF.load(custom_sample("External/external.glb"))

        # Assert
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIsInstance(resource, ExternalResource)
        self.assertEqual(external_uri, resource.uri)
        # For now, attempting to access the resource data should throw a ValueError
        with self.assertRaises(ValueError):
            _ = resource.data

    def test_convert_to_file_resource_does_nothing_if_resource_is_already_file_resource_and_uri_matches(self):
        """
        Ensures GLTF.convert_to_file_resource does nothing if the resource is already a FileResource with the same URI.
        """
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[resource])

        # Act
        converted_resource = gltf.convert_to_file_resource(resource, "buffer.bin")

        # Assert
        self.assertIs(resource, converted_resource)
        self.assertIsInstance(converted_resource, FileResource)
        self.assertEqual("buffer.bin", converted_resource.filename)
        self.assertEqual("buffer.bin", gltf.model.buffers[0].uri)

    def test_convert_to_file_resource_updates_uri_if_resource_is_already_file_resource_and_uri_is_different(self):
        """
        Ensures GLTF.convert_to_file_resource updates the filename on all buffers and images that reference the
        URI if the resource is already a FileResource but the URI is different.
        """
        # Arrange
        # Binary resource
        binary_data = b"sample binary data"
        binary_data_bytelen = len(binary_data)
        binary_data_old_uri = "buffer.bin"
        binary_data_new_uri = "buffer_updated.bin"
        binary_resource = FileResource(binary_data_old_uri, data=binary_data)
        # Image resource
        image_data = b"sample image data"
        image_old_uri = "image.png"
        image_new_uri = "image_updated.png"
        image_resource = FileResource(image_old_uri, data=image_data)
        # Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(uri=binary_data_old_uri, byteLength=binary_data_bytelen)],
            images=[Image(uri=image_old_uri, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[binary_resource, image_resource])

        # Act
        converted_binary_resource = gltf.convert_to_file_resource(binary_resource, binary_data_new_uri)
        converted_image_resource = gltf.convert_to_file_resource(image_resource, image_new_uri)

        # Assert
        # Ensure there are still 2 resources
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(converted_binary_resource in gltf.resources)
        self.assertTrue(converted_image_resource in gltf.resources)
        # Ensure both resource are still FileResource instances
        self.assertIsInstance(converted_binary_resource, FileResource)
        self.assertIsInstance(converted_image_resource, FileResource)
        # Ensure resource URIs are updated
        self.assertEqual(binary_data_new_uri, converted_binary_resource.filename)
        self.assertEqual(image_new_uri, converted_image_resource.filename)
        # Ensure buffers and images are updated with new URIs
        self.assertEqual(binary_data_new_uri, gltf.model.buffers[0].uri)
        self.assertEqual(image_new_uri, gltf.model.images[0].uri)

    def test_convert_base64_resource_to_file_resource(self):
        """Ensures GLTF.convert_to_file_resource can convert a Base64Resource to a FileResource"""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        base64_resource = Base64Resource(data, "application/octet-stream")
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri=base64_resource.uri, byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[base64_resource])
        exported_uri = "test_convert_base64_resource_to_file_resource.bin"

        # Act
        converted_resource = gltf.convert_to_file_resource(base64_resource, exported_uri)

        # Assert
        self.assertEqual(1, len(gltf.resources))
        self.assertIsInstance(converted_resource, FileResource)
        self.assertEqual(exported_uri, converted_resource.filename)
        self.assertEqual(exported_uri, gltf.model.buffers[0].uri)
        # File should not be created until model is saved
        self.assertFalse(path.exists(exported_uri))

    def test_convert_glb_resource_to_file_resource(self):
        """Ensures GLTF.convert_to_file_resource can convert a GLBResource to a FileResource"""
        # Arrange
        gltf = GLTF.load(sample("BoxTextured", "glTF-Binary"))
        # Ensure there is 1 resource to begin with
        self.assertEqual(1, len(gltf.resources))
        glb_resource = gltf.get_glb_resource()
        uri = "test_convert_glb_resource_to_file_resource.bin"

        # Act
        converted_resource = gltf.convert_to_file_resource(glb_resource, uri)

        # Assert
        # GLB resource should no longer exist since it was converted and nothing should refer to it anymore
        self.assertIsNone(gltf.get_glb_resource())
        # There should now be a single FileResource
        self.assertEqual(1, len(gltf.resources))
        self.assertIsInstance(converted_resource, FileResource)
        self.assertEqual(uri, converted_resource.filename)
        self.assertEqual(uri, converted_resource.uri)
        # There should be 1 buffer, and it should have its URI defined (the old GLB buffer should no longer be present)
        self.assertEqual(1, len(gltf.model.buffers))
        buffer = gltf.model.buffers[0]
        self.assertEqual(uri, buffer.uri)
        # Byte length should be preserved on both the buffer and FileResource
        self.assertEqual(5176, buffer.byteLength)
        self.assertEqual(5176, len(converted_resource.data))

    def test_convert_external_resource_to_file_resource_should_raise_error(self):
        """
        Ensures GLTF.convert_to_file_resource raises an error when attempting to convert an ExternalResource to a
        FileResource (loading external data is not supported for now)
        """
        # Arrange
        image_uri = "http://www.example.com/image.jpg"
        data_uri = "http://www.example.com/data.bin"
        gltf = GLTF.load(custom_sample("External/external.gltf"))
        image_resource = next(r for r in gltf.resources if r.uri == image_uri)
        data_resource = next(r for r in gltf.resources if r.uri == data_uri)

        # Act/Assert
        with self.assertRaises(ValueError):
            _ = gltf.convert_to_file_resource(image_resource, "image.png")
        with self.assertRaises(ValueError):
            _ = gltf.convert_to_file_resource(data_resource, "data.bin")

    def test_convert_to_file_resource_raises_error_if_resource_is_not_in_model(self):
        """Ensures GLTF.convert_to_file_resource raises an error if the resource is not part of the model."""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[])

        # Act/Assert
        with self.assertRaises(RuntimeError):
            _ = gltf.convert_to_file_resource(resource, "buffer.bin")

    def test_convert_to_base64_resource_does_nothing_if_resource_is_already_base64_resource(self):
        """Ensures GLTF.convert_to_base64_resource does nothing if the resource is already a Base64Resource"""
        # Arrage
        data = b"sample binary data"
        bytelen = len(data)
        base64_resource = Base64Resource(data, "application/octet-stream")
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri=base64_resource.uri, byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[base64_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(base64_resource)

        # Assert
        self.assertIs(converted_resource, base64_resource)
        self.assertIsInstance(converted_resource, Base64Resource)
        self.assertEqual(1, len(gltf.resources))
        self.assertEqual(base64_resource.uri, gltf.model.buffers[0].uri)

    def test_convert_file_resource_to_base64(self):
        """Ensures GLTF.convert_to_base64_resource can convert a FileResource to a Base64Resource"""
        # Arrage
        data = b"sample binary data"
        bytelen = len(data)
        file_resource = FileResource("sample.bin", data=data, mimetype="application/octet-stream")
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri=file_resource.uri, byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[file_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(file_resource)

        # Assert
        self.assertIsInstance(converted_resource, Base64Resource)
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIs(resource, converted_resource)
        self.assertEqual("data:application/octet-stream;base64,c2FtcGxlIGJpbmFyeSBkYXRh", gltf.model.buffers[0].uri)

    def test_convert_file_resource_to_base64_loads_file_resource_if_not_loaded(self):
        """
        Ensures GLTF.convert_to_base64_resource loads the FileResource when converting to a Base64Resource if the
        FileResource was not initially loaded.
        """
        # Arrange
        gltf = GLTF.load(sample("TriangleWithoutIndices"), load_file_resources=False)
        file_resource = gltf.get_resource("triangleWithoutIndices.bin")
        self.assertIsInstance(file_resource, FileResource)
        self.assertFalse(file_resource.loaded)

        # Act
        gltf.convert_to_base64_resource(file_resource)

        # Assert
        self.assertTrue(file_resource.loaded)

    def test_convert_image_file_resource_to_base64_updates_image_uri(self):
        """Ensures when converting a FileResource to a Base64Resource, the URI is updated on the image directly."""
        # Arrange
        image_uri = "sample.png"
        image_data = b"sample image data"
        image_resource = FileResource(image_uri, data=image_data)
        model = GLTFModel(asset=Asset(version="2.0"), images=[Image(uri=image_uri)])
        gltf = GLTF(model=model, resources=[image_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(image_resource, "image/png")

        # Assert
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIsInstance(resource, Base64Resource)
        self.assertIs(converted_resource, resource)
        self.assertEqual("data:image/png;base64,c2FtcGxlIGltYWdlIGRhdGE=", resource.uri)
        self.assertEqual("data:image/png;base64,c2FtcGxlIGltYWdlIGRhdGE=", gltf.model.images[0].uri)
        self.assertEqual("image/png", resource.mime_type)

    def test_convert_glb_resource_to_base64(self):
        """Ensures GLTF.convert_to_base64_resource can convert a GLBResource to a Base64Resource"""
        # Arrange
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(byteLength=4)],
            bufferViews=[BufferView(buffer=0)],
            accessors=[Accessor(bufferView=0)],
        )
        glb_resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[glb_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(glb_resource)

        # Assert
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIs(resource, converted_resource)
        self.assertIsInstance(resource, Base64Resource)
        self.assertEqual("data:application/octet-stream;base64,ZGF0YQ==", resource.uri)
        self.assertEqual("data:application/octet-stream;base64,ZGF0YQ==", model.buffers[0].uri)
        self.assertEqual(b"data", resource.data)

    def test_convert_glb_resource_to_base64_updates_image_uri_and_removes_buffer_view_for_embedded_images(self):
        """
        Ensures when converting a GLBResource containing an image to a Base64Resource, the image URI is updated and
        the corresponding buffer view is removed (if not referenced elsewhere). Indices for other buffer views are
        updated appropriately.
        """
        # Arrange
        # Image data and GLB resource
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # GLB Resource
        glb_resource = GLBResource(image_data)
        # Another external file resource containing other data
        binary_data = b"sample binary data"
        binary_data_bytelen = len(binary_data)
        file_resource_uri = "sample.bin"
        file_resource = FileResource(file_resource_uri, data=binary_data)
        # Create model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            accessors=[
                Accessor(bufferView=0, componentType=999, count=1, type="foo"),
                Accessor(
                    bufferView=2,
                    componentType=999,
                    count=1,
                    type="bar",
                    sparse=Sparse(
                        count=1,
                        indices=SparseIndices(bufferView=3, byteOffset=0, componentType=1),
                        values=SparseValues(bufferView=4, byteOffset=0),
                    ),
                ),
            ],
            buffers=[Buffer(byteLength=image_bytelen), Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen)],
            bufferViews=[
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
                BufferView(buffer=1, byteOffset=6, byteLength=4),
                BufferView(buffer=1, byteOffset=10, byteLength=6),
                BufferView(buffer=1, byteOffset=16, byteLength=2),
            ],
            images=[Image(bufferView=1, mimeType="image/png"), Image(bufferView=3, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[glb_resource, file_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(glb_resource)

        # Assert
        # There should be 2 resources, the converted Base64Resource and the original FileResource
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(file_resource in gltf.resources)
        base64_resource = next((r for r in gltf.resources if isinstance(r, Base64Resource)), None)
        self.assertIsNotNone(base64_resource)
        self.assertIsInstance(base64_resource, Base64Resource)
        self.assertIs(converted_resource, base64_resource)
        # Ensure Base64Resource URI is correct
        self.assertEqual(b"sample image data", base64_resource.data)
        self.assertEqual("data:application/octet-stream;base64,c2FtcGxlIGltYWdlIGRhdGE=", base64_resource.uri)
        # There should now be one buffer for the external file resource
        self.assertEqual(1, len(gltf.model.buffers))
        self.assertEqual(Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen), gltf.model.buffers[0])
        # There should now be 4 buffer views (the buffer view for the image should be removed). The remaining ones
        # should have the buffer index changed to reflect the removed buffer.
        self.assertEqual(
            [
                BufferView(buffer=0, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=6, byteLength=4),
                BufferView(buffer=0, byteOffset=10, byteLength=6),
                BufferView(buffer=0, byteOffset=16, byteLength=2),
            ],
            gltf.model.bufferViews,
        )
        # Image should now have a data URI instead of referencing a buffer view
        self.assertEqual("data:application/octet-stream;base64,c2FtcGxlIGltYWdlIGRhdGE=", gltf.model.images[0].uri)
        self.assertIsNone(gltf.model.images[0].bufferView)
        # Accessors that reference a buffer view after the one that was removed should have their indices updated
        self.assertEqual(
            [
                Accessor(bufferView=0, componentType=999, count=1, type="foo"),
                Accessor(
                    bufferView=1,
                    componentType=999,
                    count=1,
                    type="bar",
                    sparse=Sparse(
                        count=1,
                        indices=SparseIndices(bufferView=2, byteOffset=0, componentType=1),
                        values=SparseValues(bufferView=3, byteOffset=0),
                    ),
                ),
            ],
            gltf.model.accessors,
        )
        # Images that reference a buffer view after the one that was removed should have their indices updated
        self.assertEqual(2, gltf.model.images[1].bufferView)

    def test_convert_glb_resource_to_base64_leaves_buffer_view_if_referenced_elsewhere(self):
        """
        Ensures when converting a GLBResource containing an image to a Base64Resource, the corresponding buffer view for
        the image is retained if it is referenced elsewhere.
        """
        # Arrange
        # Image data and GLB resource
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # GLB Resource
        glb_resource = GLBResource(image_data)
        # Another external file resource containing other data
        binary_data = b"sample binary data"
        binary_data_bytelen = len(binary_data)
        file_resource_uri = "sample.bin"
        file_resource = FileResource(file_resource_uri, data=binary_data)
        # Create model. Note accessor references the same buffer view as embedded image. Maybe not a very realistic
        # scenario, but in this case the buffer view should be retained when the image is converted.
        model = GLTFModel(
            asset=Asset(version="2.0"),
            accessors=[Accessor(bufferView=1, componentType=999, count=1, type="foo")],
            buffers=[Buffer(byteLength=image_bytelen), Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen)],
            bufferViews=[
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
            ],
            images=[Image(bufferView=1, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[glb_resource, file_resource])

        # Act
        converted_resource = gltf.convert_to_base64_resource(glb_resource)

        # Assert
        # There should be 2 resources, the converted Base64Resource and the original FileResource
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(file_resource in gltf.resources)
        base64_resource = next((r for r in gltf.resources if isinstance(r, Base64Resource)), None)
        self.assertIsNotNone(base64_resource)
        self.assertIsInstance(base64_resource, Base64Resource)
        self.assertIs(converted_resource, base64_resource)
        # Ensure Base64Resource URI is correct
        self.assertEqual(b"sample image data", base64_resource.data)
        expected_uri = "data:application/octet-stream;base64,c2FtcGxlIGltYWdlIGRhdGE="
        self.assertEqual(expected_uri, base64_resource.uri)
        # There should be two buffers, one that now has Base64 data URI, and another for file resource that wasn't
        # converted.
        self.assertEqual(2, len(gltf.model.buffers))
        self.assertEqual(Buffer(uri=expected_uri, byteLength=image_bytelen), gltf.model.buffers[0])
        self.assertEqual(Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen), gltf.model.buffers[1])
        # There should still be 2 buffer views (i.e., the buffer view for the image should NOT be removed in this case
        # since it is also referenced by an accessor)
        self.assertEqual(
            [
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
            ],
            gltf.model.bufferViews,
        )
        # Image should continue to reference the buffer view since it wasn't removed
        self.assertIsNone(gltf.model.images[0].uri)
        self.assertEqual(1, gltf.model.images[0].bufferView)
        # Accessors should be retained (buffer views indices should not be updated since no buffer views were removed)
        self.assertEqual(1, len(gltf.model.accessors))
        self.assertEqual(Accessor(bufferView=1, componentType=999, count=1, type="foo"), gltf.model.accessors[0])

    def test_convert_external_resource_to_base64_resource_should_raise_error(self):
        """
        Ensures GLTF.convert_to_base64_resource raises an error when attempting to convert an ExternalResource to a
        Base64Resource (loading external data is not supported for now)
        """
        # Arrange
        image_uri = "http://www.example.com/image.jpg"
        data_uri = "http://www.example.com/data.bin"
        gltf = GLTF.load(custom_sample("External/external.gltf"))
        image_resource = next(r for r in gltf.resources if r.uri == image_uri)
        data_resource = next(r for r in gltf.resources if r.uri == data_uri)

        # Act/Assert
        with self.assertRaises(ValueError):
            _ = gltf.convert_to_base64_resource(image_resource)
        with self.assertRaises(ValueError):
            _ = gltf.convert_to_base64_resource(data_resource)

    def test_convert_to_base64_resource_raises_error_if_resource_is_not_in_model(self):
        """Ensures GLTF.convert_to_base64_resource raises an error if the resource is not part of the model."""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[])

        # Act/Assert
        with self.assertRaises(RuntimeError):
            _ = gltf.convert_to_base64_resource(resource, "buffer.bin")

    def test_convert_to_external_resource_does_nothing_if_resource_is_already_external_resource_and_uri_matches(self):
        """
        Ensures GLTF.convert_to_external_resource does nothing if the resource is already an ExternalResource with the
        same URI.
        """
        # Arrange
        uri = "http://www.example.com/data.bin"
        resource = ExternalResource("http://www.example.com/data.bin")
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri=uri, byteLength=123)])
        gltf = GLTF(model=model, resources=[resource])

        # Act
        converted_resource = gltf.convert_to_external_resource(resource, uri)

        # Assert
        self.assertIs(resource, converted_resource)
        self.assertIsInstance(converted_resource, ExternalResource)
        self.assertEqual(uri, converted_resource.uri)
        self.assertEqual(uri, gltf.model.buffers[0].uri)

    def test_convert_to_external_resource_updates_uri_if_resource_is_already_file_resource_and_uri_is_different(self):
        """
        Ensures GLTF.convert_to_external_resource updates the URI on all buffers and images that reference the
        URI if the resource is already an ExternalResource but the URI is different.
        """
        # Arrange
        # Binary resource
        binary_data_old_uri = "http://www.example.com/data.bin"
        binary_data_new_uri = "http://www.example.com/data_updated.bin"
        binary_resource = ExternalResource(binary_data_old_uri)
        # Image resource
        image_old_uri = "http://www.example.com/image.png"
        image_new_uri = "http://www.example.com/image_updated.png"
        image_resource = ExternalResource(image_old_uri)
        # Model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(uri=binary_data_old_uri, byteLength=123)],
            images=[Image(uri=image_old_uri, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[binary_resource, image_resource])

        # Act
        converted_binary_resource = gltf.convert_to_external_resource(binary_resource, binary_data_new_uri)
        converted_image_resource = gltf.convert_to_external_resource(image_resource, image_new_uri)

        # Assert
        # Ensure there are still 2 resources
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(converted_binary_resource in gltf.resources)
        self.assertTrue(converted_image_resource in gltf.resources)
        # Ensure both resource are still ExternalResource instances
        self.assertIsInstance(converted_binary_resource, ExternalResource)
        self.assertIsInstance(converted_image_resource, ExternalResource)
        # Ensure resource URIs are updated
        self.assertEqual(binary_data_new_uri, converted_binary_resource.uri)
        self.assertEqual(image_new_uri, converted_image_resource.uri)
        # Ensure buffers and images are updated with new URIs
        self.assertEqual(binary_data_new_uri, gltf.model.buffers[0].uri)
        self.assertEqual(image_new_uri, gltf.model.images[0].uri)

    def test_convert_image_file_resource_to_external(self):
        """Ensures when converting a FileResource to an ExternalResource, the URI is updated on the image directly."""
        # Arrange
        image_filename = "sample.png"
        image_data = b"sample image data"
        image_resource = FileResource(image_filename, data=image_data)
        model = GLTFModel(asset=Asset(version="2.0"), images=[Image(uri=image_filename)])
        gltf = GLTF(model=model, resources=[image_resource])

        # Act
        image_uri = "http://www.example.com/image.png"
        converted_resource = gltf.convert_to_external_resource(image_resource, image_uri)

        # Assert
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIsInstance(resource, ExternalResource)
        self.assertIs(converted_resource, resource)
        self.assertEqual(image_uri, resource.uri)
        self.assertEqual(image_uri, gltf.model.images[0].uri)

    def test_convert_base64_resource_to_external(self):
        """Ensures a Base64Resource can be converted to an ExternalResource"""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        base64_resource = Base64Resource(data, "application/octet-stream")
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri=base64_resource.uri, byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[base64_resource])

        # Act
        exported_uri = "http://www.example.com/data.bin"
        converted_resource = gltf.convert_to_external_resource(base64_resource, exported_uri)

        # Assert
        self.assertEqual(1, len(gltf.resources))
        self.assertIsInstance(converted_resource, ExternalResource)
        self.assertEqual(exported_uri, converted_resource.uri)
        self.assertEqual(exported_uri, gltf.model.buffers[0].uri)

    def test_convert_glb_resource_to_external(self):
        """Ensures GLTF.convert_to_external_resource can convert a GLBResource to an ExternalResource"""
        # Arrange
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[Buffer(byteLength=4)],
            bufferViews=[BufferView(buffer=0)],
            accessors=[Accessor(bufferView=0)],
        )
        glb_resource = GLBResource(b"data")
        gltf = GLTF(model=model, resources=[glb_resource])

        # Act
        exported_uri = "http://www.example.com/data.bin"
        converted_resource = gltf.convert_to_external_resource(glb_resource, exported_uri)

        # Assert
        self.assertEqual(1, len(gltf.resources))
        resource = gltf.resources[0]
        self.assertIs(resource, converted_resource)
        self.assertIsInstance(resource, ExternalResource)
        self.assertEqual(exported_uri, resource.uri)
        self.assertEqual(exported_uri, model.buffers[0].uri)

    def test_convert_glb_resource_to_external_updates_image_uri_and_removes_buffer_view_for_embedded_images(self):
        """
        Ensures when converting a GLBResource containing an image to an ExternalResource, the image URI is updated and
        the corresponding buffer view is removed (if not referenced elsewhere). Indices for other buffer views are
        updated appropriately.
        """
        # Arrange
        # Image data and GLB resource
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # GLB Resource
        glb_resource = GLBResource(image_data)
        # Another external file resource containing other data
        binary_data = b"sample binary data"
        binary_data_bytelen = len(binary_data)
        file_resource_uri = "sample.bin"
        file_resource = FileResource(file_resource_uri, data=binary_data)
        # Create model
        model = GLTFModel(
            asset=Asset(version="2.0"),
            accessors=[
                Accessor(bufferView=0, componentType=999, count=1, type="foo"),
                Accessor(
                    bufferView=2,
                    componentType=999,
                    count=1,
                    type="bar",
                    sparse=Sparse(
                        count=1,
                        indices=SparseIndices(bufferView=3, byteOffset=0, componentType=1),
                        values=SparseValues(bufferView=4, byteOffset=0),
                    ),
                ),
            ],
            buffers=[Buffer(byteLength=image_bytelen), Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen)],
            bufferViews=[
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
                BufferView(buffer=1, byteOffset=6, byteLength=4),
                BufferView(buffer=1, byteOffset=10, byteLength=6),
                BufferView(buffer=1, byteOffset=16, byteLength=2),
            ],
            images=[Image(bufferView=1, mimeType="image/png"), Image(bufferView=3, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[glb_resource, file_resource])

        # Act
        exported_uri = "http://www.example.com/data.bin"
        converted_resource = gltf.convert_to_external_resource(glb_resource, exported_uri)

        # Assert
        # There should be 2 resources, the converted ExternalResource and the original FileResource
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(file_resource in gltf.resources)
        external_resource = next((r for r in gltf.resources if isinstance(r, ExternalResource)), None)
        self.assertIsNotNone(external_resource)
        self.assertIsInstance(external_resource, ExternalResource)
        self.assertIs(converted_resource, external_resource)
        # Ensure ExternalResource URI is correct
        self.assertEqual(exported_uri, external_resource.uri)
        # There should now be one buffer for the external file resource
        self.assertEqual(1, len(gltf.model.buffers))
        self.assertEqual(Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen), gltf.model.buffers[0])
        # There should now be 4 buffer views (the buffer view for the image should be removed). The buffer index should
        # be changed to 0 since the first buffer was removed.
        self.assertEqual(
            [
                BufferView(buffer=0, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=6, byteLength=4),
                BufferView(buffer=0, byteOffset=10, byteLength=6),
                BufferView(buffer=0, byteOffset=16, byteLength=2),
            ],
            gltf.model.bufferViews,
        )
        # Image should now have an external URI instead of referencing a buffer view
        self.assertEqual(exported_uri, gltf.model.images[0].uri)
        self.assertIsNone(gltf.model.images[0].bufferView)
        # Accessors that reference a buffer view after the one that was removed should have their indices updated
        self.assertEqual(
            [
                Accessor(bufferView=0, componentType=999, count=1, type="foo"),
                Accessor(
                    bufferView=1,
                    componentType=999,
                    count=1,
                    type="bar",
                    sparse=Sparse(
                        count=1,
                        indices=SparseIndices(bufferView=2, byteOffset=0, componentType=1),
                        values=SparseValues(bufferView=3, byteOffset=0),
                    ),
                ),
            ],
            gltf.model.accessors,
        )
        # Images that reference a buffer view after the one that was removed should have their indices updated
        self.assertEqual(2, gltf.model.images[1].bufferView)

    def test_convert_glb_resource_to_external_leaves_buffer_view_if_referenced_elsewhere(self):
        """
        Ensures when converting a GLBResource containing an image to an ExternalResource, the corresponding buffer view
        for the image is retained if it is referenced elsewhere.
        """
        # Arrange
        # Image data and GLB resource
        image_data = b"sample image data"
        image_bytelen = len(image_data)
        # GLB Resource
        glb_resource = GLBResource(image_data)
        # Another external file resource containing other data
        binary_data = b"sample binary data"
        binary_data_bytelen = len(binary_data)
        file_resource_uri = "sample.bin"
        file_resource = FileResource(file_resource_uri, data=binary_data)
        # Create model. Note accessor references the same buffer view as embedded image. Maybe not a very realistic
        # scenario, but in this case the buffer view should be retained when the image is converted.
        model = GLTFModel(
            asset=Asset(version="2.0"),
            accessors=[Accessor(bufferView=1, componentType=999, count=1, type="foo")],
            buffers=[Buffer(byteLength=image_bytelen), Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen)],
            bufferViews=[
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
            ],
            images=[Image(bufferView=1, mimeType="image/png")],
        )
        gltf = GLTF(model=model, resources=[glb_resource, file_resource])

        # Act
        exported_uri = "http://www.example.com/data.bin"
        converted_resource = gltf.convert_to_external_resource(glb_resource, exported_uri)

        # Assert
        # There should be 2 resources, the converted ExternalResource and the original FileResource
        self.assertEqual(2, len(gltf.resources))
        self.assertTrue(file_resource in gltf.resources)
        external_resource = next((r for r in gltf.resources if isinstance(r, ExternalResource)), None)
        self.assertIsNotNone(external_resource)
        self.assertIsInstance(external_resource, ExternalResource)
        self.assertIs(converted_resource, external_resource)
        # Ensure ExternalResource URI is correct
        self.assertEqual(exported_uri, external_resource.uri)
        # There should be two buffers, one that now has an external URI, and another for file resource that wasn't
        # converted.
        self.assertEqual(2, len(gltf.model.buffers))
        self.assertEqual(Buffer(uri=exported_uri, byteLength=image_bytelen), gltf.model.buffers[0])
        self.assertEqual(Buffer(uri=file_resource_uri, byteLength=binary_data_bytelen), gltf.model.buffers[1])
        # There should still be 2 buffer views (i.e., the buffer view for the image should NOT be removed in this case
        # since it is also referenced by an accessor)
        self.assertEqual(
            [
                BufferView(buffer=1, byteOffset=0, byteLength=6),
                BufferView(buffer=0, byteOffset=0, byteLength=image_bytelen),
            ],
            gltf.model.bufferViews,
        )
        # Image should continue to reference the buffer view since it wasn't removed
        self.assertIsNone(gltf.model.images[0].uri)
        self.assertEqual(1, gltf.model.images[0].bufferView)
        # Accessors should be retained (buffer views indices should not be updated since no buffer views were removed)
        self.assertEqual(1, len(gltf.model.accessors))
        self.assertEqual(Accessor(bufferView=1, componentType=999, count=1, type="foo"), gltf.model.accessors[0])

    def test_convert_to_external_resource_raises_error_if_resource_is_not_in_model(self):
        """Ensures GLTF.convert_to_external_resource raises an error if the resource is not part of the model."""
        # Arrange
        data = b"sample binary data"
        bytelen = len(data)
        resource = FileResource("buffer.bin", data=data)
        model = GLTFModel(asset=Asset(version="2.0"), buffers=[Buffer(uri="buffer.bin", byteLength=bytelen)])
        gltf = GLTF(model=model, resources=[])

        # Act/Assert
        with self.assertRaises(RuntimeError):
            _ = gltf.convert_to_external_resource(resource, "buffer.bin")

    def test_import_empty_binary_chunk(self):
        """Ensures a GLB file with a binary chunk having zero byte length can be loaded"""
        # Act
        glb = GLTF.load(custom_sample("EmptyChunk/EmptyBinaryChunk.glb"))

        # Assert
        self.assertEqual(1, len(glb.resources))
        resource = glb.resources[0]
        self.assertIsInstance(resource, GLBResource)
        self.assertEqual(b"", resource.data)

    def test_load_glb_unexpected_eof_in_json_chunk_emits_warning(self):
        """
        Ensures loading a GLB with unexpected EOF in JSON chunk body emits a warning. As long as the JSON can still be
        parsed successfully, no error should be raised.
        """
        # Act/Assert
        with self.assertWarnsRegex(RuntimeWarning, "Unexpected EOF when parsing JSON chunk body"):
            glb = GLTF.load(custom_sample("Corrupt/JsonChunkEOF.glb"))
            self.assertEqual(GLTFModel(asset=Asset(version="2.0")), glb.model)

    def test_load_glb_unexpected_eof_in_binary_chunk_body_emits_warning(self):
        """Ensures loading a GLB with unexpected EOF in binary chunk body emits a warning."""
        # Act/Assert
        with self.assertWarnsRegex(RuntimeWarning, "Unexpected EOF when parsing binary chunk body"):
            glb = GLTF.load(custom_sample("Corrupt/BinaryChunkEOF.glb"))
            self.assertEqual(GLTFModel(asset=Asset(version="2.0")), glb.model)

    def test_gltf_wrong_encoding(self):
        """
        Per the spec, glTF must use UTF-8 encoding without BOM for JSON data. However, the library should be forgiving
        and still allow opening glTF files that were saved with the wrong encoding, as long as they can still be parsed
        successfully. Any characters that could not be read will be replaced with a question mark.

        This test ensures that non-binary (glTF) files with wrong encoding can be read successfully. See next test for
        binary GLB files with wrong encoding in the JSON chunk.
        """
        # Act
        utf8_bom = GLTF.load(custom_sample("BadEncoding/gltf/utf-8-bom.gltf"))
        utf16_le = GLTF.load(custom_sample("BadEncoding/gltf/utf-16-le.gltf"))
        utf16_be = GLTF.load(custom_sample("BadEncoding/gltf/utf-16-be.gltf"))
        windows1252 = GLTF.load(custom_sample("BadEncoding/gltf/windows-1252.gltf"))

        # Assert
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf8_bom.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf16_le.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf16_be.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0", copyright="�Test� � Company")), windows1252.model)

    def test_glb_wrong_encoding(self):
        """
        Per the spec, glTF must use UTF-8 encoding without BOM for JSON data. However, the library should be forgiving
        and still allow opening glTF files that were saved with the wrong encoding, as long as they can still be parsed
        successfully. Any characters that could not be read will be replaced with a question mark.

        This test validates that the JSON chunk inside a binary GLB can still be read even if it is saved with the wrong
        encoding. See previous test for non-binary (glTF) files with wrong encoding.
        """
        # Act
        utf8_bom = GLTF.load(custom_sample("BadEncoding/glb/utf-8-bom.glb"))
        utf16_le = GLTF.load(custom_sample("BadEncoding/glb/utf-16-le.glb"))
        utf16_be = GLTF.load(custom_sample("BadEncoding/glb/utf-16-be.glb"))
        windows1252 = GLTF.load(custom_sample("BadEncoding/glb/windows-1252.glb"))

        # Assert
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf8_bom.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf16_le.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0")), utf16_be.model)
        self.assertEqual(GLTFModel(asset=Asset(version="2.0", copyright="�Test� � Company")), windows1252.model)

    def test_gltf_windows_1252(self):
        """
        Test manually specifying an encoding (Windows-1252) when reading glTF.

        Per the spec, glTF must use UTF-8 encoding without BOM for JSON data. However, the library should be forgiving
        and still allow opening glTF files that were saved with the wrong encoding, as long as they can still be parsed
        successfully. Any characters that could not be read will be replaced with a question mark.

        In this example, the glTF file is saved using Windows-1252 encoding, and uses quote and dash characters from the
        Windows-1252 code page. Ensure these characters can be read out successfully, in this case without being
        replaced by question marks since the encoding was specified when loading the file.
        """
        # Act
        gltf = GLTF.load(custom_sample("BadEncoding/gltf/windows-1252.gltf"), encoding="cp1252")

        # Assert
        self.assertEqual(GLTFModel(asset=Asset(version="2.0", copyright="“Test” – Company")), gltf.model)

    def test_glb_windows_1252(self):
        """
        Test manually specifying an encoding (Windows-1252) when reading GLB.

        Per the spec, glTF must use UTF-8 encoding without BOM for JSON data. However, the library should be forgiving
        and still allow opening glTF files that were saved with the wrong encoding, as long as they can still be parsed
        successfully. Any characters that could not be read will be replaced with a question mark.

        In this example, the JSON chunk inside the GLB file is encoded using Windows-1252, and uses quote and dash
        characters from the Windows-1252 code page. Ensure these characters can be read out successfully, in this case
        without being replaced by question marks since the encoding was specified when loading the file.
        """
        # Act
        gltf = GLTF.load(custom_sample("BadEncoding/glb/windows-1252.glb"), encoding="cp1252")

        # Assert
        self.assertEqual(GLTFModel(asset=Asset(version="2.0", copyright="“Test” – Company")), gltf.model)

    def test_uri_encoding_save_mixed(self):
        """
        URIs may be encoded and not encoded (see https://github.com/KhronosGroup/glTF/issues/1449).
        """
        # Act
        file_resource = FileResource("File Resource.bin", data=b"")
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=file_resource.filename, byteLength=0),
                Buffer(uri=file_resource.uri, byteLength=0),
            ],
        )
        gltf = GLTF(model=model, resources=[file_resource])

        # Act/Assert
        with tempfile.TemporaryDirectory() as temp_dir:
            gltf.export(path.join(temp_dir, "uri_encoding_save_mixed.glb"))

    def test_uri_encoding_validate_mixed_base64(self):
        """
        URIs may be encoded and not encoded (see https://github.com/KhronosGroup/glTF/issues/1449).
        """
        # Act
        file_resource = FileResource("File Resource.bin", data=b"")
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=file_resource.filename, byteLength=0),
                Buffer(uri=file_resource.uri, byteLength=0),
            ],
        )
        gltf = GLTF(model=model, resources=[file_resource])

        # Act/Assert
        gltf._validate_resources()

        # Act/Assert
        gltf.convert_to_base64_resource(file_resource)
        gltf._validate_resources()

    def test_uri_encoding_validate_mixed_embed(self):
        """
        URIs may be encoded and not encoded (see https://github.com/KhronosGroup/glTF/issues/1449).
        """
        # Act
        file_resource = FileResource("File Resource.bin", data=b"")
        model = GLTFModel(
            asset=Asset(version="2.0"),
            buffers=[
                Buffer(uri=file_resource.filename, byteLength=0),
                Buffer(uri=file_resource.uri, byteLength=0),
            ],
        )
        gltf = GLTF(model=model, resources=[file_resource])

        # Act/Assert
        gltf._validate_resources()

        # Act/Assert
        gltf.embed_resource(file_resource)
        gltf._validate_resources()
