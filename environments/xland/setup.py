from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules = cythonize("generation/world/wfc/wfc_binding.pyx", annotate=False),
    include_dirs=[],
    zip_safe=False,
)