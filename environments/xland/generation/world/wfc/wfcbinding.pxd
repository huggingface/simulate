# distutils: language=c++

cdef extern from "cpp/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef int main(unsigned width, unsigned height)