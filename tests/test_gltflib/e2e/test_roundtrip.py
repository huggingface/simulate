import subprocess
import tempfile
from os import path
from pathlib import Path
from pprint import pformat
from unittest import TestCase

from simulate.assets.gltflib import GLTF

from ..util import SIMULATE_TEST_REPOS, sample


# If set to True, for any models that fail to pass the equality check, this will automatically launch kdiff3 to compare
# the original model to the roundtrip model (execution will be paused while kdiff3 is open).
DEBUG = False


class TestRoundtrip(TestCase):
    """
    Performs round-trip equality tests for all models in the glTF-Sample-Models repository.

    This test class loads each model (including all variants: glTF, glTF-Binary, glTF-Embedded, etc.) from the original
    glTF-Sample-Models repository, then performs the following steps:

      1. Export the model (without any changes) to a temporary location
      2. Load the exported copy
      3. Ensure that the parsed model from the exported copy is equal to the parsed model from the original sample

    This ensures that all fields were parsed correctly and that no fields are missing.
    """

    @classmethod
    def setUpClass(cls):
        print()
        print("Running round-trip tests:")
        print()

    def setUp(self):
        self.maxDiff = None

    def _get_model_index(self):
        return SIMULATE_TEST_REPOS

    def test_roundtrip(self):
        """Ensures all sample models remain unchanged after loading, saving, and loading again via the library"""

        # Read the model-index.json file to get a listing of all sample models
        for model_name in self._get_model_index():
            original_filename = sample(model_name)

            # Parse the original model
            original_model = GLTF.load(original_filename)

            # Export a copy of the parsed model to a temporary location
            with tempfile.TemporaryDirectory() as temp_dir:
                output_filename = path.join(temp_dir, model_name + ".gltf")
                original_model.export(output_filename)

                # Parse the exported copy
                roundtrip_model = GLTF.load(output_filename)

                # In debug mode, open a diff viewer if the original model is not equivalent to the roundtrip version
                if DEBUG and original_model.model != roundtrip_model.model:
                    self._launch_diff_viewer(original_filename, original_model, roundtrip_model)

                # Fail the test if the original model doesn't match the roundtrip model
                self.assertEqual(original_model.model, roundtrip_model.model)

    def _launch_diff_viewer(self, filename: str, model_1: GLTF, model_2: GLTF):
        """Helper method to open a diff viewer if the models don't match"""
        p = Path(filename)
        basename = p.stem
        ext = p.suffix
        v1 = pformat(model_1.model.to_dict())
        v2 = pformat(model_2.model.to_dict())
        with tempfile.NamedTemporaryFile(mode="w+", prefix=f"{basename}_original_", suffix=ext) as f1:
            f1.write(v1)
            f1.flush()
            with tempfile.NamedTemporaryFile(mode="w+", prefix=f"{basename}_roundtrip_", suffix=ext) as f2:
                f2.write(v2)
                f2.flush()
                subprocess.run(["kdiff3", f1.name, f2.name])
