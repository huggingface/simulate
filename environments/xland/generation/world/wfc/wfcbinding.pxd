# distutils: language=c++
from libcpp cimport bool

cdef extern from "cpp/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef int main(unsigned int width, unsigned int height, bool periodic_output)