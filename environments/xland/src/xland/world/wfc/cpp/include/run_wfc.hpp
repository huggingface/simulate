#pragma once

#include "rapidxml_utils.hpp"

// TODO: use namespace wfc
using namespace std;
using namespace rapidxml;

std::vector<Color> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<Color> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, string dir_path);