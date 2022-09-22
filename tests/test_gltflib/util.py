import os
from os import path

from huggingface_hub import hf_hub_download

from simulate.assets.gltflib import GLTF, FileResource


# Directory containing the official glTF sample files. These samples are the same ones that are available here:
# https://github.com/KhronosGroup/glTF-Sample-Models
SIMULATE_TEST_URL = "simulate-tests/"

SIMULATE_TEST_REPOS = [
    "AnimatedCube",
    "Box",
    "BoxTextured",
    # "Box_With_Spaces",
    "TriangleWithoutIndices",
]

# Custom sample models used for tests
CUSTOM_SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples", "custom")


def get_file_from_hub(model, filename, subfolder=None):
    """
    Helper function for downloading a file from the hub.
    :param repo_id: Repository ID
    :param filename: Filename
    :param subfolder: Subfolder (optional)
    :return: File path
    """
    return hf_hub_download(
        repo_id=SIMULATE_TEST_URL + model,
        filename=filename,
        subfolder=subfolder,
        repo_type="space",
    )


def sample(model, fmt="glTF"):
    """
    Helper function for returning the path to an official sample model from the glTF-Sample-Models directory in the
    specified format (defaults to glTF).
    :param model: Model name
    :param fmt: Format (either 'glTF', 'glTF-Binary', 'glTF-Embedded', or 'glTF-Draco'. Defaults to 'glTF')
    :return: Model filename
    """
    ext = ".glb" if fmt == "glTF-Binary" else ".gltf"

    repo_id = model
    filename = model + ext
    subfolder = fmt

    # Download the main file
    file_path = get_file_from_hub(repo_id, filename, subfolder)

    # Let's download/cache all the other needed ressources
    gltf_scene = GLTF.load(file_path)
    if repo_id is not None:
        for ressource in gltf_scene.resources:
            if isinstance(ressource, FileResource):
                _ = get_file_from_hub(repo_id, ressource.filename, subfolder)
    return file_path


def custom_sample(filename):
    """
    Helper function for returning the path to a custom sample model (as opposed to an official sample model from the
    glTF-Sample-Models repository, as returned by sample). This simply adds the CUSTOM_SAMPLES_DIR base directory to
    the specified path.
    :param filename: Filename of the sample model. This should also include the subdirectory (e.g.,
        "Minimal/minimal.gltf")
    :return: Full filename for the custom model
    """
    return path.join(CUSTOM_SAMPLES_DIR, filename)
