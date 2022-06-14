# Lint as: python3
""" HuggingFace/xland is a procedurally generated environment for RL.

Note:

   VERSION needs to be formatted following the MAJOR.MINOR.PATCH convention
   (we need to follow this convention to be able to retrieve versioned scripts)

Simple check list for release from AllenNLP repo: https://github.com/allenai/allennlp/blob/main/setup.py

To create the package for pypi.

0. Prerequisites:
   - Dependencies:
     - twine: "pip install twine"
   - Create an account in (and join the 'simenv' project):
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
   pip install -i https://testpypi.python.org/pypi simenv

6. Upload the final version to actual pypi:
   twine upload dist/* -r pypi

7. Fill release notes in the tag in github once everything is looking hunky-dory.

8. Change the version in __init__.py and setup.py to X.X.X+1.dev0 (e.g. VERSION=1.18.3 -> 1.18.4.dev0).
   Then push the change with a message 'set dev version'
"""

import os
import sys
from distutils.extension import Extension

from Cython.Build import cythonize
from setuptools import find_packages, setup

REQUIRED_PKGS = [
    "dataclasses_json",  # For GLTF export/imports
    "numpy>=1.17",  # We use numpy>=1.17 to have np.random.Generator
    "simenv",
]

QUALITY_REQUIRE = ["black~=22.0", "flake8>=3.8.3", "isort>=5.0.0", "pyyaml>=5.3.1"]

TESTS_REQUIRE = [
    # test dependencies
]

EXTRAS_REQUIRE = {
    "dev": TESTS_REQUIRE + QUALITY_REQUIRE,
    "tests": TESTS_REQUIRE,
    "quality": QUALITY_REQUIRE,
}

# We build fastwfc
BUILD_CYTHON = True

if sys.platform == 'win32':
    # TODO: Work in progress
    pass

elif sys.platform == 'darwin':
   PROFILE_FILE = "~/.zprofile"
   VARIABLE_NAME = "DLYD_LIBRARY_PATH"

elif sys.platform.startswith('linux'):   # 'linux' on Py3, 'linux2' on Py2
   PROFILE_FILE = "~/.bashrc"
   VARIABLE_NAME = "LD_LIBRARY_PATH"
   
else:
   BUILD_CYTHON = False
   print("Unsupported platform. Skipping cython generation...")

if BUILD_CYTHON:
   try:
      print("Building fastwfc...")
      assert os.system("cmake src/xland/world/wfc/cpp/fastwfc/. -Bsrc/xland/world/wfc/cpp/fastwfc/.") == 0
      assert os.system("make -C src/xland/world/wfc/cpp/fastwfc/") == 0
      print("Done!")

   except:
      if not os.path.exists("src/xland/world/wfc/cpp/fastwfc/lib"):
         print("Error building external library, please create fastwfc manually.")
         sys.exit(1)

   ext_modules = [
    Extension(
        name="wfc_binding",
        sources=["src/xland/world/wfc/wfc_binding.pyx"],
        language="c++",
        extra_compile_args=["-std=c++17"],
        extra_link_args=["-std=c++17"],
        libraries=["fastwfc"],
        library_dirs=["src/xland/world/wfc/cpp/fastwfc/lib"],
        include_dirs=[
            "src/xland/world/wfc/cpp/fastwfc/src/include",
            os.path.join(os.getcwd(), "src/xland/world/wfc/cpp/include"),
        ],  # path to .h file(s)
      )
   ]

   ext_modules = cythonize(ext_modules, force=True)

else:
   ext_modules = None

setup(
    name="xland",
    description="HuggingFace procedurally generated environment for RL.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="HuggingFace Inc.",
    author_email="alicia@huggingface.co",
    license="Apache 2.0",
    version="0.0.1.dev0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=REQUIRED_PKGS,
    extras_require=EXTRAS_REQUIRE,
    ext_modules=ext_modules,
    keywords="simulation environments procedural generation reinforcement machine learning",
    zip_safe=False,
)

# Add the path to the library to the environment variable
export_command = "export {}=src/xland/world/wfc/cpp/fastwfc/lib:${}".format(
            VARIABLE_NAME, VARIABLE_NAME)

# Set bashrc
assert os.system("echo \"{} \">>{}".format(
            export_command, PROFILE_FILE)) == 0

# You should run export in current session and avoid using source / exec
print("Run {} for updating current shell.".format(export_command))