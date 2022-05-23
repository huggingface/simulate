# distutils: language=c++

from wfcbinding cimport main


def py_main(unsigned width, unsigned height):
    main(width, height)