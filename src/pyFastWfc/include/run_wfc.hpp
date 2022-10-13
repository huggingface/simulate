#ifndef FAST_WFC_RUN_WFC
#define FAST_WFC_RUN_WFC
#include <string>
#include <vector>
#include "id_pair.hpp"

#pragma once

// TODO: use namespace wfc
// using namespace std;


struct Neighbor {
    std::string left, right;
    unsigned left_or, right_or;
};

struct PyTile {
     unsigned size;
     std::vector<IdPair> tile;
     std::string name;
     std::string symmetry;
     double weight;
};

std::vector<IdPair> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<IdPair> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors);

#endif // FAST_WFC_RUN_WFC