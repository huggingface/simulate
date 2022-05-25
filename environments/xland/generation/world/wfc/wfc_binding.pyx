# distutils: language=c++

from libcpp cimport bool, str
from wfcbinding cimport main


def run_wfc(unsigned width, unsigned height, int sample_type, bool periodic_output=True, unsigned N=3,
            bool periodic_input=False, bool ground=False, unsigned nb_samples=1, unsigned symmetry=8, int seed=0, 
            bool use_seed=False):
    
    main(use_seed, seed, width, height, sample_type, periodic_output, N, periodic_input, ground, nb_samples, symmetry) 