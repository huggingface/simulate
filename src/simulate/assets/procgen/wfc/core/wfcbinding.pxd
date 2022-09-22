# distutils: language=c++
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


cdef extern from "cpp/include/id_pair.hpp":
    cdef struct IdPair:
        unsigned uid, rotation, reflected

cdef extern from "cpp/src/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef struct Neighbor:
        string left, right
        unsigned left_or, right_or

    cdef struct PyTile:
        unsigned size
        vector[IdPair] tile
        string name
        string symmetry
        double weight

    cdef vector[IdPair] run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output, 
                    unsigned N, bool periodic_input, bool ground, unsigned nb_samples,
                    unsigned symmetry, vector[IdPair] input_img, 
                    unsigned input_width, unsigned input_height, bool verbose, 
                    unsigned nb_tries, vector[PyTile] tiles,
                    vector[Neighbor] neighbors)
