#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <limits>
#include "time.h"

#include "include/run_wfc.hpp"
#include "fastwfc/src/include/overlapping_wfc.hpp"
#include "fastwfc/src/include/tiling_wfc.hpp"
#include "fastwfc/src/include/utils/array3D.hpp"
#include "fastwfc/src/include/wfc.hpp"
#include "include/color.hpp"
#include "include/utils.hpp"
#include <unordered_set>

using namespace std;

/**
 * Get a random seed.
 * This function use random_device on linux, but use the C rand function for
 * other targets. This is because, for instance, windows don't implement
 * random_device non-deterministically.
 */
int get_random_seed() {
  #ifdef __linux__
    return random_device()();
  #else
    return rand();
  #endif
}

/**
 * Get next seed for the random number generator.
 * Increases the seed in 1 if it's less than the maximum unsigned int.
 * Otherwise, it resets the seed to 0.
 */
unsigned increment_seed(unsigned seed) {
  if (seed < numeric_limits<unsigned>::max() - 1) {
    return seed + 1;
  } else {
    return 0;
  }
}

/*
* Function to create Array2D from vector of vectors.
*/
Array2D<Color> array2d_from_vector(std::vector<Color> input, unsigned width, unsigned height) {
  Array2D<Color> arr = Array2D<Color>(height, width);
  arr.data = input;
  return arr;
}

/**
 * Read the overlapping wfc problem.
 */
std::optional<std::vector<Color>> read_overlapping_instance(unsigned seed, unsigned width, 
                              unsigned height, bool periodic_output, unsigned N,
                              bool periodic_input, bool ground, unsigned nb_samples, 
                              unsigned symmetry, std::vector<Color> input_img,
                              unsigned input_width, unsigned input_height,
                              bool verbose, unsigned nb_tries) {
                                
  if (verbose) {
    cout << "Started!" << endl;
  }

  // Stop hardcoding samples
  std::optional<Array2D<Color>> m = array2d_from_vector(input_img, input_width, input_height);
  if (!m.has_value()) {
    throw "Error while loading the map to sample from.";
  }

  OverlappingWFCOptions options = {
      periodic_input, periodic_output, height, width, symmetry, ground, N};
  for (unsigned i = 0; i < nb_samples; i++) {
    for (unsigned test = 0; test < nb_tries; test++) {
      if (test > 0) {
        seed = increment_seed(seed);
      }
      OverlappingWFC<Color> wfc(*m, options, seed);
      std::optional<Array2D<Color>> success = wfc.run();
      if (success.has_value()) {
        if (verbose) {
          cout << "Finished!" << endl;
        }
        return success.value().data;
      } else {
        if (verbose) {
          cout << "Failed to generate!" << endl;
        }
      }
    }
  }
}

/**
 * Transform a symmetry name into its Symmetry enum
 */
Symmetry to_symmetry(const string &symmetry_name) {
  if (symmetry_name == "X") {
    return Symmetry::X;
  }
  if (symmetry_name == "T") {
    return Symmetry::T;
  }
  if (symmetry_name == "I") {
    return Symmetry::I;
  }
  if (symmetry_name == "L") {
    return Symmetry::L;
  }
  if (symmetry_name == "\\") {
    return Symmetry::backslash;
  }
  if (symmetry_name == "P") {
    return Symmetry::P;
  }
  throw symmetry_name + "is an invalid Symmetry";
}

// Convert PyTile to Tile
Tile<Color> pytile_to_tile(PyTile pytile) {
  // Only accepts square tiles for now
  Array2D<Color> image = array2d_from_vector(pytile.tile, pytile.size, pytile.size);
  Tile<Color> tile (image, to_symmetry(pytile.symmetry), pytile.weight);
  return tile;
}

/**
 * Read an instance of a tiling WFC problem.
 */
std::optional<std::vector<Color>> read_simpletiled_instance(unsigned seed, unsigned width, unsigned height, bool periodic_output,
                                bool verbose, unsigned nb_tries, std::vector<PyTile> pytiles,
                                std::vector<Neighbor> neighbors) noexcept {

  if (verbose) {
    cout << "Started!" << endl;
  }

  unordered_map<string, unsigned> tiles_id;
  vector<Tile<Color>> tiles;
  unsigned id = 0;

  for (unsigned i = 0; i < pytiles.size(); i++) {
    tiles_id.insert({pytiles[i].name, id});
    tiles.push_back(pytile_to_tile(pytiles[i]));
    id++;
  }

  vector<tuple<unsigned, unsigned, unsigned, unsigned>> neighbors_ids;
  for (auto neighbor : neighbors) {
    const string &neighbor1 = neighbor.left;
    const int &orientation1 = neighbor.left_or;
    const string &neighbor2 = neighbor.right;
    const int &orientation2 = neighbor.right_or;
    if (tiles_id.find(neighbor1) == tiles_id.end()) {
      continue;
    }
    if (tiles_id.find(neighbor2) == tiles_id.end()) {
      continue;
    }
    neighbors_ids.push_back(make_tuple(tiles_id[neighbor1], orientation1,
                                       tiles_id[neighbor2], orientation2));
  }

  for (unsigned test = 0; test < 10; test++) {
    if (test > 0) {
      seed = increment_seed(seed);
    }
    
    TilingWFC<Color> wfc(tiles, neighbors_ids, height, width, {periodic_output},
                         seed);

    std::optional<Array2D<Color>> success = wfc.run();
    if (success.has_value()) {
      if (verbose) {
        cout << "Finished!" << endl;
      }
      return success.value().data;
    } else {
      if (verbose) {
        cout << "Failed!" << endl;
      }
    }
  }
}

// TODO: try adding &
/**
 * Valid tiles corresponds to array with the tiles, size of tiles, names, symmetries, and weights.
 * For neighbors: vector of tuples (left, orientation, right, orientation).
 */
std::vector<Color> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, 
        bool periodic_output, unsigned N, bool periodic_input, bool ground, 
        unsigned nb_samples, unsigned symmetry,
        std::vector<Color> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, 
        std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors) {

  // Initialize rand for non-linux targets
  #ifndef __linux__
    srand(time(nullptr));
  #endif

  std::chrono::time_point<std::chrono::system_clock> start, end;
  start = std::chrono::system_clock::now();

  std::optional<std::vector<Color>> success;

  if (sample_type == 0) {
    success = read_simpletiled_instance(seed, width, height, periodic_output, verbose, nb_tries,
                                        tiles, neighbors);
  }

  else if (sample_type == 1) {
    success = read_overlapping_instance(seed, width, height, periodic_output, N, periodic_input, ground, 
                  nb_samples, symmetry, input_img, input_width, input_height, verbose, nb_tries);
  }

  else {
    throw "choose 0 (simpletiled) or 1 (overlapping) on sample_type";
  }

  end = std::chrono::system_clock::now();
  int elapsed_s =
      std::chrono::duration_cast<std::chrono::seconds>(end - start).count();
  int elapsed_ms =
      std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
          .count();
  if (verbose) {
    std::cout << "All samples done in " << elapsed_s << "s, " << elapsed_ms % 1000
            << "ms.\n";
  }

  if (success.has_value()) {
    return success.value();
  } else {
    return std::vector<Color>();
  }
}
