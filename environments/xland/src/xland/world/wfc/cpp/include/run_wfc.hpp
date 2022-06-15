#pragma once

#include "rapidxml_utils.hpp"

// TODO: use namespace wfc
using namespace std;
using namespace rapidxml;


struct Neighbor {
    string left, right;
    unsigned left_or, right_or;
};

struct PyTile {
     unsigned size;
     std::vector<Color> tile;
     string name;
     Symmetry symmetry;
     double weight;
};

std::vector<Color> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<Color> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, string dir_path, std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors);