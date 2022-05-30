#pragma once

#include "rapidxml_utils.hpp"

// TODO: use namespace wfc
using namespace std;
using namespace rapidxml;

int run_wfc_cpp(bool use_seed, int seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry, string input_img);