# distutils: language=c++

from libcpp cimport bool
from libcpp.string cimport string
from wfcbinding cimport run_wfc_cpp


def run_wfc(unsigned width, unsigned height, int sample_type, string input_img=b"", bool periodic_output=True, unsigned N=3,
            bool periodic_input=False, bool ground=False, unsigned nb_samples=1, unsigned symmetry=8, int seed=0, 
            bool use_seed=False, bool verbose=False, unsigned nb_tries=10, string dir_path=".gen_files"):

    run_wfc_cpp(use_seed, seed, width, height, sample_type, periodic_output, N, periodic_input, ground, nb_samples, symmetry, input_img,
                verbose, nb_tries, dir_path)