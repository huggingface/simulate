#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "include/id_pair.hpp"
#include "include/run_wfc.hpp"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

py::array_t<unsigned> run_wfc(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<IdPair> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors) {

    // if neighbors == None:
    //     neighbors = []

    // if tiles == None:
    //     tiles = []

    // if input_img == None:
    //     input_img = []

    // As we are using a different convention from the library, we pass width as height and height as width.
    // The same applies to the input image.
    std::vector<IdPair> result;

    result = run_wfc_cpp(seed, height, width, sample_type, periodic_output, N, periodic_input, ground, 
                nb_samples, symmetry, input_img, input_height, input_width,
                verbose, nb_tries, tiles, neighbors);

    if (result.size() == 0) {
        throw std::invalid_argument("ERROR: Wave Function Collapse failed. \nTips: Use smaller width / height; Use larger \
        image as input (overlapping case); or relax restrictions (simpletiled) by increasing the number \
        of possible neighbors.");
    }

	// Build our output arrays from VHACD outputs
    py::array_t<unsigned> np_results = py::array_t<unsigned>(result.size() * 3);
	py::buffer_info buf_np_results = np_results.request();
    unsigned *ptr_np_results = (unsigned *) buf_np_results.ptr;

    for (uint32_t j = 0; j < result.size(); j++)
    {
        ptr_np_results[3*j] = result[j].uid;
        ptr_np_results[3*j+1] = result[j].rotation;
        ptr_np_results[3*j+2] = result[j].reflected;
    }

    // Reshape the array to be (nb_samples, width, height, 3)
    const long n_attributes = 3;
    np_results.resize({(long)nb_samples, (long)width, (long)height, n_attributes});

    return np_results;
}

PYBIND11_MODULE(pyFastWfc, m) {
    m.doc() = R"pbdoc(
        python bindings for fast-wfc
        -----------------------

        .. currentmodule:: pyfastwfc

        .. autosummary::
           :toctree: _generate
    )pbdoc";

    py::class_<IdPair>(m, "IdPair")
        .def(py::init<const unsigned, const unsigned, const unsigned>())
        .def_readwrite("uid", &IdPair::uid)
        .def_readwrite("rotation", &IdPair::rotation)
        .def_readwrite("reflected", &IdPair::reflected);
    
    py::class_<PyTile>(m, "PyTile")
        .def(py::init<const unsigned, const std::vector<IdPair> &, const std::string &, const std::string &, const double>())
        .def_readwrite("size", &PyTile::size)
        .def_readwrite("tile", &PyTile::tile)
        .def_readwrite("name", &PyTile::name)
        .def_readwrite("symmetry", &PyTile::symmetry)
        .def_readwrite("weight", &PyTile::weight);

    py::class_<Neighbor>(m, "Neighbor")
        .def(py::init<>())
        .def_readwrite("left", &Neighbor::left)
        .def_readwrite("right", &Neighbor::right)
        .def_readwrite("left_or", &Neighbor::left_or)
        .def_readwrite("right_or", &Neighbor::right_or);
    
    m.def("run_wfc", &run_wfc, R"pbdoc(
        Run the Wave Function Collapse algorithm.

        Args:
            width (int): Width of the output image.
            height (int): Height of the output image.
            sample_type (int): Type of samples. 0: simpletiled, 1: overlapping.
            input_img (list): Input image. If not provided, the algorithm will generate a new image.
            input_width (int): Width of the input image.
            input_height (int): Height of the input image.
            periodic_output (bool): Whether the output image is periodic.
            N (int): Number of possible neighbors for each tile.
            periodic_input (bool): Whether the input image is periodic.
            ground (bool): Whether to use ground tiles.
            nb_samples (int): Number of samples to generate.
            symmetry (int): Symmetry of the tiles. 1: no symmetry, 2: 180 degree rotation, 4: 90 degree rotation, 8: 45 degree rotation.
            seed (int): Seed for the random number generator.
            verbose (bool): Whether to print debug information.
            nb_tries (int): Number of tries before giving up.
            tiles (list): List of tiles.
            neighbors (list): List of neighbors.

        Returns:
            list: List of samples.
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif

}
