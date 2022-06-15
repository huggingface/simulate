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
#include "include/external/rapidxml.hpp"
#include "include/image.hpp"
#include "include/rapidxml_utils.hpp"
#include "include/utils.hpp"
#include <unordered_set>

using namespace rapidxml;
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
                              const string &current_dir, bool verbose, unsigned nb_tries) {
                                
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

/**
 * Read the names of the tiles in the subset in a tiling WFC problem
 */
std::optional<unordered_set<string>> read_subset_names(xml_node<> *root_node,
                                                       const string &subset) {
  unordered_set<string> subset_names;
  xml_node<> *subsets_node = root_node->first_node("subsets");
  if (!subsets_node) {
    return std::nullopt;
  }
  xml_node<> *subset_node = subsets_node->first_node("subset");
  while (subset_node &&
         rapidxml::get_attribute(subset_node, "name") != subset) {
    subset_node = subset_node->next_sibling("subset");
  }
  if (!subset_node) {
    return std::nullopt;
  }
  for (xml_node<> *node = subset_node->first_node("tile"); node;
       node = node->next_sibling("tile")) {
    subset_names.insert(rapidxml::get_attribute(node, "name"));
  }
  return subset_names;
}

/**
 * Read all tiles for a tiling problem
 */
unordered_map<string, Tile<Color>> read_tiles(xml_node<> *root_node,
                                              const string &current_dir,
                                              const string &subset,
                                              unsigned size) {
  std::optional<unordered_set<string>> subset_names =
      read_subset_names(root_node, subset);
  unordered_map<string, Tile<Color>> tiles;
  xml_node<> *tiles_node = root_node->first_node("tiles");
  for (xml_node<> *node = tiles_node->first_node("tile"); node;
       node = node->next_sibling("tile")) {
    string name = rapidxml::get_attribute(node, "name");
    if (subset_names != nullopt &&
        subset_names->find(name) == subset_names->end()) {
      continue;
    }
    Symmetry symmetry =
        to_symmetry(rapidxml::get_attribute(node, "symmetry", "X"));
    double weight = stod(rapidxml::get_attribute(node, "weight", "1.0"));
    const std::string image_path = current_dir + "/" + name + ".png";
    optional<Array2D<Color>> image = read_image(image_path);

    if (image == nullopt) {
      vector<Array2D<Color>> images;
      for (unsigned i = 0; i < nb_of_possible_orientations(symmetry); i++) {
        const std::string image_path =
            current_dir + "/" + name + " " + to_string(i) + ".png";
        optional<Array2D<Color>> image = read_image(image_path);
        if (image == nullopt) {
          throw "Error while loading " + image_path;
        }
        if ((image->width != size) || (image->height != size)) {
          throw "Image " + image_path + " has wrong size";
        }
        images.push_back(*image);
      }
      Tile<Color> tile = {images, symmetry, weight};
      tiles.insert({name, tile});
    } else {
      if ((image->width != size) || (image->height != size)) {
        throw "Image " + image_path + " has wrong size";
      }

      Tile<Color> tile(*image, symmetry, weight);
      tiles.insert({name, tile});
    }
  }

  return tiles;
}

/**
 * Read the neighbors constraints for a tiling problem.
 * A value {t1,o1,t2,o2} means that the tile t1 with orientation o1 can be
 * placed at the right of the tile t2 with orientation o2.
 */
vector<tuple<string, unsigned, string, unsigned>>
read_neighbors(xml_node<> *root_node) {
  vector<tuple<string, unsigned, string, unsigned>> neighbors;
  xml_node<> *neighbor_node = root_node->first_node("neighbors");
  for (xml_node<> *node = neighbor_node->first_node("neighbor"); node;
       node = node->next_sibling("neighbor")) {
    string left = rapidxml::get_attribute(node, "left");
    string::size_type left_delimiter = left.find(" ");
    string left_tile = left.substr(0, left_delimiter);
    unsigned left_orientation = 0;
    if (left_delimiter != string::npos) {
      left_orientation = stoi(left.substr(left_delimiter, string::npos));
    }

    string right = rapidxml::get_attribute(node, "right");
    string::size_type right_delimiter = right.find(" ");
    string right_tile = right.substr(0, right_delimiter);
    unsigned right_orientation = 0;
    if (right_delimiter != string::npos) {
      right_orientation = stoi(right.substr(right_delimiter, string::npos));
    }
    neighbors.push_back(
        {left_tile, left_orientation, right_tile, right_orientation});
  }
  return neighbors;
}

/**
 * Read an instance of a tiling WFC problem.
 */
std::optional<std::vector<Color>> read_simpletiled_instance(unsigned seed, unsigned width, unsigned height, bool periodic_output,
                               const string &current_dir, bool verbose, unsigned nb_tries) noexcept {
  string name = "tiles";
  string subset = "tiles";

  if (verbose) {
    cout << "Started!" << endl;
  }

  ifstream config_file(current_dir + "/" + name + "/data.xml");
  vector<char> buffer((istreambuf_iterator<char>(config_file)),
                      istreambuf_iterator<char>());
  buffer.push_back('\0');
  xml_document<> data_document;
  data_document.parse<0>(&buffer[0]);
  xml_node<> *data_root_node = data_document.first_node("set");
  unsigned size = stoi(rapidxml::get_attribute(data_root_node, "size"));


  unordered_map<string, Tile<Color>> tiles_map =
      read_tiles(data_root_node, current_dir + "/" + name, subset, size);
  unordered_map<string, unsigned> tiles_id;
  vector<Tile<Color>> tiles;
  unsigned id = 0;
  for (pair<string, Tile<Color>> tile : tiles_map) {
    tiles_id.insert({tile.first, id});
    tiles.push_back(tile.second);
    id++;
  }

  vector<tuple<string, unsigned, string, unsigned>> neighbors =
      read_neighbors(data_root_node);
  vector<tuple<unsigned, unsigned, unsigned, unsigned>> neighbors_ids;
  for (auto neighbor : neighbors) {
    const string &neighbor1 = get<0>(neighbor);
    const int &orientation1 = get<1>(neighbor);
    const string &neighbor2 = get<2>(neighbor);
    const int &orientation2 = get<3>(neighbor);
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
        bool verbose, unsigned nb_tries, string dir_path, 
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
    success = read_simpletiled_instance(seed, width, height, periodic_output, dir_path, verbose, nb_tries);
  }

  else if (sample_type == 1) {
    success = read_overlapping_instance(seed, width, height, periodic_output, N, periodic_input, ground, 
                  nb_samples, symmetry, input_img, input_width, input_height, dir_path, verbose, nb_tries);
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
