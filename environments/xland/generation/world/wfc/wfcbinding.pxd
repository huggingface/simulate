# distutils: language=c++

cdef extern from "cpp/lib/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp" namespace "wfc":
    cdef int main()