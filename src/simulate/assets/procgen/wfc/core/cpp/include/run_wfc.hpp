#pragma once

// TODO: use namespace wfc
using namespace std;


struct Neighbor {
    string left, right;
    unsigned left_or, right_or;
};

struct PyTile {
     unsigned size;
     std::vector<IdPair> tile;
     string name;
     string symmetry;
     double weight;
};

std::vector<IdPair> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<IdPair> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors);