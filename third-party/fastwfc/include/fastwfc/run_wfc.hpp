#ifndef FAST_WFC_RUN_WFC
#define FAST_WFC_RUN_WFC
#include <string>
#include <vector>
#include "utils/array2D.hpp"

#pragma once

namespace fastwfc {

/**
 * Represent a 24-bit rgb color.
 */
struct IdPair {
  unsigned uid, rotation, reflected;

  bool operator==(const IdPair &obj) const noexcept {
    return uid == obj.uid && rotation == obj.rotation && reflected == obj.reflected;
  }

  bool operator!=(const IdPair &obj) const noexcept { return !(obj == *this); }
};

struct Neighbor {
    std::string left, right;
    unsigned left_or, right_or;
};

struct PyTile {
     unsigned size;
     std::vector<IdPair> tile;
     std::string name;
     std::string symmetry;
     double weight;
};

std::vector<IdPair> run_wfc_cpp(unsigned seed, unsigned width, unsigned height, int sample_type, bool periodic_output,
        unsigned N, bool periodic_input, bool ground, unsigned nb_samples, unsigned symmetry,
        std::vector<IdPair> input_img, unsigned input_width, unsigned input_height, 
        bool verbose, unsigned nb_tries, std::vector<PyTile> tiles,
        std::vector<Neighbor> neighbors);

} // namespace fastwfc

/**
 * Override rotated and reflected methods on Array2D for IdPairs
 */
template<> inline Array2D<fastwfc::IdPair> Array2D<fastwfc::IdPair>::rotated() const noexcept {
  Array2D<fastwfc::IdPair> result = Array2D<fastwfc::IdPair>(width, height);
    for (std::size_t y = 0; y < width; y++) {
      for (std::size_t x = 0; x < height; x++) {

        fastwfc::IdPair original = get(x, width - 1 - y);

        if(original.reflected == 1) {
          original.rotation = (original.rotation + 3) % 4;
        } else {
          original.rotation = (original.rotation + 1) % 4;
        }

        result.get(y, x) = original;
      }
    }
    return result;
}

template<> inline Array2D<fastwfc::IdPair> Array2D<fastwfc::IdPair>::reflected() const noexcept {
  Array2D<fastwfc::IdPair> result = Array2D<fastwfc::IdPair>(width, height);
    for (std::size_t y = 0; y < height; y++) {
      for (std::size_t x = 0; x < width; x++) {
        fastwfc::IdPair original = get(y, width - 1 - x);
        original.reflected = (original.reflected + 1) % 2;
        result.get(y, x) = original;
      }
    }
    return result;
}

/**
 * Hash function for Id Pair.
 */
namespace std {
    template <> class hash<fastwfc::IdPair> {
    public:
      size_t operator()(const fastwfc::IdPair &obj) const {
        // TODO: create exception for overflow
        // 8 different types of orientations (1 - 8 with 1 and 8 included)
        // We limit the number of different tiles to 536870911
        // Otherwise, there is overflow on the hash function
        return (size_t) (obj.rotation + 4 * obj.reflected) * (size_t) 536870911 + (size_t) obj.uid;
      }
    };
} // namespace std

#endif // FAST_WFC_RUN_WFC