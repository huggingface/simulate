#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "run_wfc.hpp"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;
using namespace pybind11::literals;

py::array_t<unsigned> run_wfc(unsigned seed, unsigned width, unsigned height, int sample_type,
        bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<fastwfc::IdPair> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, std::vector<fastwfc::PyTile> tiles,
        std::vector<fastwfc::Neighbor> neighbors) {

    // As we are using a different convention from the library, we pass width as height and height as width.
    // The same applies to the input image.
    std::vector<fastwfc::IdPair> result;

    result = fastwfc::run_wfc_cpp(seed, height, width, sample_type, periodic_output, N, periodic_input, ground, 
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

PYBIND11_MODULE(_fastwfc, m) {
    m.doc() = R"pbdoc(
        python bindings for fast-wfc
        -----------------------

        .. currentmodule:: fastwfc

        .. autosummary::
           :toctree: _generate
    )pbdoc";

    py::class_<fastwfc::IdPair>(m, "IdPair")
        .def(py::init<const unsigned, const unsigned, const unsigned>(),
            "uid"_a, "rotation"_a, "reflected"_a)
        .def_readwrite("uid", &fastwfc::IdPair::uid)
        .def_readwrite("rotation", &fastwfc::IdPair::rotation)
        .def_readwrite("reflected", &fastwfc::IdPair::reflected);
    
    py::class_<fastwfc::PyTile>(m, "PyTile")
        .def(py::init<const unsigned, const std::vector<fastwfc::IdPair> &, const std::string &,
            const std::string &, const double>(),
            "size"_a, "tile"_a, "name"_a, "symmetry"_a, "weight"_a)
        .def_readwrite("size", &fastwfc::PyTile::size)
        .def_readwrite("tile", &fastwfc::PyTile::tile)
        .def_readwrite("name", &fastwfc::PyTile::name)
        .def_readwrite("symmetry", &fastwfc::PyTile::symmetry)
        .def_readwrite("weight", &fastwfc::PyTile::weight);

    py::class_<fastwfc::Neighbor>(m, "Neighbor")
        .def(py::init<const std::string, const std::string, const unsigned, const unsigned>(),
            "left"_a, "right"_a, "left_or"_a, "right_or"_a)
        .def_readwrite("left", &fastwfc::Neighbor::left)
        .def_readwrite("right", &fastwfc::Neighbor::right)
        .def_readwrite("left_or", &fastwfc::Neighbor::left_or)
        .def_readwrite("right_or", &fastwfc::Neighbor::right_or);
    
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
    )pbdoc", "seed"_a, "width"_a, "height"_a, "sample_type"_a,
    "periodic_output"_a, "N"_a, "periodic_input"_a, "ground"_a,
    "nb_samples"_a, "symmetry"_a, "input_img"_a, "input_width"_a,
    "input_height"_a, "verbose"_a, "nb_tries"_a, "tiles"_a, "neighbors"_a);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif

}
