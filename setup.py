# Lint as: python3
""" HuggingFace/simulate is an open library of simulation and synthetic environments.

Note:

    VERSION needs to be formatted following the MAJOR.MINOR.PATCH convention
    (we need to follow this convention to be able to retrieve versioned scripts)

Simple check list for release from AllenNLP repo: https://github.com/allenai/allennlp/blob/main/setup.py

To create the package for pypi.

0. Prerequisites:
    - Dependencies:
      - twine: "pip install twine"
    - Create an account in (and join the 'simulate' project):
      - PyPI: https://pypi.org/
      - Test PyPI: https://test.pypi.org/

1. Change the version in:
    - __init__.py
    - setup.py

2. Commit these changes: "git commit -m 'Release: VERSION'"

3. Add a tag in git to mark the release: "git tag VERSION -m 'Add tag VERSION for pypi'"
    Push the tag to remote: git push --tags origin main

4. Build both the sources and the wheel. Do not change anything in setup.py between
    creating the wheel and the source distribution (obviously).

    First, delete any "build" directory that may exist from previous builds.

    For the wheel, run: "python setup.py bdist_wheel" in the top level directory.
    (this will build a wheel for the python version you use to build it).

    For the sources, run: "python setup.py sdist"
    You should now have a /dist directory with both .whl and .tar.gz source versions.

5. Check that everything looks correct by uploading the package to the pypi test server:

    twine upload dist/* -r pypitest --repository-url=https://test.pypi.org/legacy/

    Check that you can install it in a virtualenv/notebook by running:
    pip install -i https://testpypi.python.org/pypi simulate

6. Upload the final version to actual pypi:
    twine upload dist/* -r pypi

7. Fill release notes in the tag in GitHub once everything is looking hunky-dory.

8. Change the version in __init__.py and setup.py to X.X.X+1.dev0 (e.g. VERSION=1.18.3 -> 1.18.4.dev0).
    Then push the change with a message 'set dev version'
"""
from skbuild import setup

import numpy as np
from glob import glob

# Available at setup time due to pyproject.toml
# from pybind11.setup_helpers import Pybind11Extension, build_ext

from setuptools import find_packages
import sys

__version__ = "0.0.3.dev0"  # expected format is one of x.y.z.dev0, or x.y.z.rc1 or x.y.z (no to dashes, yes to dots)

REQUIRED_PKGS = [
    "dataclasses_json",  # For GLTF export/imports
    "numpy>=1.18",  # We use numpy>=1.17 to have np.random.Generator
    "vtk>=9.0",  # Pyvista doesn't always install vtk, so we do it here
    "pyvista>=0.35",  # For mesh creation and edition and simple vizualization
    "huggingface_hub>=0.10",  # For sharing objects, environments & trained RL policies
    'pybind11>=2.10.0',  # For compiling extensions pybind11
    'scikit-build>=0.5',  # For compiling extensions
]

RL_REQUIRE = [
    "gym==0.21.0",  # For RL action spaces and API
]
SB3_REQUIRE = [
    "gym==0.21.0",  # For RL action spaces and API
    "stable-baselines3"
]

DEV_REQUIRE = [
    "gym==0.21.0",  # For RL action spaces and API
    "stable-baselines3",  # For training with SB3

    # For background vizualization capabilities (could be optional - note than some Qt backend can have GPL license)
    "pyvistaqt",
    "pyqt5",  # You can also use PySide2, PyQt6 or PySide6 (see https://github.com/spyder-ide/qtpy#requirements)
]

TESTS_REQUIRE = [
    "pytest",
    "pytest-xdist",

    "gym",  # For RL action spaces and API
    "stable-baselines3",  # For training with SB3
]

DOCS_REQUIRE = [
    "s3fs"
]

QUALITY_REQUIRE = ["black[jupyter]~=22.0", "flake8>=3.8.3", "isort>=5.0.0", "pyyaml>=5.3.1"]

EXTRAS_REQUIRE = {
    "rl": RL_REQUIRE,
    "sb3": SB3_REQUIRE,
    "dev": DEV_REQUIRE + TESTS_REQUIRE + QUALITY_REQUIRE,
    "test": TESTS_REQUIRE,
    "quality": QUALITY_REQUIRE,
    "docs": DOCS_REQUIRE,
}

if sys.platform == 'darwin':
    extra_compile_args = ["-std=c++11"]
    extra_link_args = ["-std=c++11"]

else:
    extra_compile_args = []
    extra_link_args = []


setup(
    name="simulate",
    version=__version__,
    description="HuggingFace community-driven open-source library of simulation environments",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="HuggingFace Inc.",
    author_email="thomas@huggingface.co",
    url="https://github.com/huggingface/simulate",
    download_url="https://github.com/huggingface/simulate/tags",
    license="Apache 2.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    package_data={'simulate': ['src/simulate/engine/*.zip']},
    install_requires=REQUIRED_PKGS,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="simulation environments synthetic data datasets machine learning",
    zip_safe=False,  # Required for mypy to find the py.typed file
    python_requires=">=3.8",
    include_dirs=[np.get_include()],
    cmake_install_dir='src/simulate',
)

# When building extension modules `cmake_install_dir` should always be set to the
# location of the package you are building extension modules for.
# Specifying the installation directory in the CMakeLists subtley breaks the relative
# paths in the helloTargets.cmake file to all of the library components.
