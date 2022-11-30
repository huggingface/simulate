#ifndef FAST_WFC_RUN_WFC
#define FAST_WFC_RUN_WFC
#include <string>
#include <vector>

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