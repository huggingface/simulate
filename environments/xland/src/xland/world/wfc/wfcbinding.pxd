# distutils: language=c++
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


cdef extern from "cpp/include/color.hpp":
    cdef struct Color:
        unsigned char r, g, b

cdef extern from "cpp/run_wfc.cpp":
    pass

cdef extern from "cpp/include/run_wfc.hpp":
    cdef struct Neighbor:
        string left, right
        unsigned left_or, right_or

    cdef struct PyTile:
        unsigned size
        vector[Color] tile
        string name
        string symmetry
        double weight

    cdef vector[Color] run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output, 
                    unsigned N, bool periodic_input, bool ground, unsigned nb_samples,
                    unsigned symmetry, vector[Color] input_img, 
                    unsigned input_width, unsigned input_height, bool verbose, 
                    unsigned nb_tries, vector[PyTile] tiles,
                    vector[Neighbor] neighbors)
