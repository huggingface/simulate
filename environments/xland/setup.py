from setuptools import setup
import os
# from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension


ext_modules = [
    Extension(
        name="wfc_binding",
        sources=["generation/world/wfc/wfc_binding.pyx"],
        language="c++",
        extra_compile_args=["-std=c++17"],
        extra_link_args=["-std=c++17"],
        libraries=["fastwfc"],
        include_dirs=[os.path.join(os.getcwd(), "generation/world/wfc/cpp/include")],  # path to .h file(s)
   )
]

ext_modules = cythonize(ext_modules)

setup(
    ext_modules=ext_modules,
    zip_safe=False,
)