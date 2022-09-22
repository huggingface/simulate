import json
from unittest import TestCase

from simulate.assets.gltflib import GLTF, Animation, AnimationSampler, Asset, Buffer, Channel, GLTFModel, Target

from ..util import sample


class TestGLTFModel(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_init(self):
        """
        Basic test ensuring the successful initialization of a GLTF2 model when all required properties are passed
        in. Note the only required property in a GLTF2 model is the asset.
        """
        # Act
        model = GLTFModel(asset=Asset())

        # Assert
        self.assertIsInstance(model, GLTFModel)

    def test_asset_version_default(self):
        """Ensures asset version is initialized as 2.0 if not passed in"""
        # Act
        model = GLTFModel(asset=Asset())

        # Assert
        self.assertEqual(model.asset.version, "2.0")

    def test_asset_version(self):
        """Ensures asset version is retained if a value is passed in"""
        # Act
        model = GLTFModel(asset=Asset(version="2.1"))

        # Assert
        self.assertEqual(model.asset.version, "2.1")

    def test_to_json_removes_properties_set_to_None(self):
        """
        Ensures that any properties in the model that are set to None are deleted when encoding the model to JSON.
        """
        # Arrange
        model = GLTFModel(asset=Asset(generator=None, minVersion=None), buffers=None)

        # Act
        v = model.to_json()

        # Assert
        data = json.loads(v)
        self.assertDictEqual(data, {"asset": {"version": "2.0"}})

    def test_to_json_retains_empty_strings_lists_and_dicts(self):
        """
        Ensures that any properties in the model that are set to an empty string, list, or dictionary are retained when
        encoding the model to JSON.
        """
        # Arrange
        model = GLTFModel(asset=Asset(generator="", minVersion=None), buffers=[], extensions={})

        # Act
        v = model.to_json()

        # Assert
        data = json.loads(v)
        self.assertDictEqual(data, {"asset": {"version": "2.0", "generator": ""}, "buffers": [], "extensions": {}})

    def test_decode(self):
        """Ensures that a simple model can be decoded successfully from JSON."""
        # Arrange
        v = '{"asset": {"version": "2.1"}, "buffers": [{ "uri": "triangle.bin", "byteLength": 44 }]}'

        # Act
        model = GLTFModel.from_json(v)

        # Assert
        self.assertEqual(
            model, GLTFModel(asset=Asset(version="2.1"), buffers=[Buffer(uri="triangle.bin", byteLength=44)])
        )

    def test_decode_missing_required_property(self):
        """
        Ensures that a warning is emitted when decoding a model from JSON if any required properties are missing.
        In this case, the "asset" property on the model is missing.
        """
        # Arrange
        v = "{}"

        # Act/Assert
        with self.assertWarnsRegex(RuntimeWarning, "non-optional type asset"):
            _ = GLTFModel.from_json(v)

    def test_load_skins(self):
        """Ensures skin data is loaded"""
        # Act
        gltf = GLTF.load(sample("RiggedSimple"))

        # Assert
        self.assertEqual(1, len(gltf.model.skins))
        skin = gltf.model.skins[0]
        self.assertEqual(9, skin.inverseBindMatrices)
        self.assertEqual(3, skin.skeleton)
        self.assertCountEqual([3, 4], skin.joints)

    def test_load_animations(self):
        """Ensures animation data is loaded correctly"""
        # Act
        gltf = GLTF.load(sample("AnimatedCube"))

        # Assert
        self.assertCountEqual(
            [
                Animation(
                    name="animation_AnimatedCube",
                    channels=[Channel(sampler=0, target=Target(node=0, path="rotation"))],
                    samplers=[AnimationSampler(input=0, interpolation="LINEAR", output=1)],
                )
            ],
            gltf.model.animations,
        )
