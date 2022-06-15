# distutils: language=c++
from libcpp cimport bool
from libcpp.string cimport string


cdef extern from "cpp/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef void run_wfc_cpp(unsigned width, unsigned height, int sample_type, bool periodic_output, 
                    unsigned N, bool periodic_input, bool ground, unsigned nb_samples,
                    unsigned symmetry, unsigned seed, string input_img, bool verbose, 
                    unsigned nb_tries, string dir_path) 
