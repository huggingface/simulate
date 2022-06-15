# distutils: language=c++

from libcpp cimport bool
from libcpp.string cimport string
from wfcbinding cimport Color, run_wfc_cpp

import numpy as np

cimport numpy as np


# It's necessary to call "import_array" if you use any part of the
# numpy PyArray_* API. From Cython 3, accessing attributes like
# ".shape" on a typed Numpy array use this API. Therefore we recommend
# always calling "import_array" whenever you "cimport numpy"
np.import_array()

# Data type of arrays
DTYPE = int

# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.int_t DTYPE_t


def run_wfc(unsigned width, unsigned height, int sample_type, list input_img=None, 
            unsigned input_width=0, unsigned input_height=0, bool periodic_output=True, unsigned N=3,
            bool periodic_input=False, bool ground=False, unsigned nb_samples=1, unsigned symmetry=8, unsigned seed=0, 
             bool verbose=False, unsigned nb_tries=10, string dir_path=".gen_files"):

    if input_img == None:
        input_img = []

    else:
        for i in range(len(input_img)):
            input_img[i] = Color(r=input_img[i][0], g=input_img[i][1], b=input_img[i][2])

    # As we are using a different convention from the library, we pass width as height and height as width.
    # The same applies to the input image.
    result = run_wfc_cpp(seed, height, width, sample_type, periodic_output, N, periodic_input, ground, 
                nb_samples, symmetry, input_img, input_height, input_width,
                verbose, nb_tries, dir_path)

    cdef np.ndarray np_results = np.array([list(r.values()) for r in result], dtype=DTYPE).reshape(width, height, -1)
    return np_results