# distutils: language=c++
from libcpp cimport bool
from libcpp.string cimport string

cdef extern from "cpp/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef int main(unsigned int width, unsigned int height, int sample_type, bool periodic_output, 
                    unsigned int N, bool periodic_input, bool ground, unsigned int nb_samples,
                    unsigned int symmetry, int seed, bool use_seed, string input_img) 
