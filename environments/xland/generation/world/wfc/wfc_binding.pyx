# distutils: language=c++

from libcpp cimport bool
from wfcbinding cimport main


def py_main(unsigned width, unsigned height, bool periodic_output):
    main(width, height, periodic_output)