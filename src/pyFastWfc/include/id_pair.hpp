#ifndef FAST_WFC_UTILS_IDPAIR_HPP_
#define FAST_WFC_UTILS_IDPAIR_HPP_

#include <functional>

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

/**
 * Hash function for Id Pair.
 */
namespace std {
template <> class hash<IdPair> {
public:
  size_t operator()(const IdPair &obj) const {
    // TODO: create exception for overflow
    // 8 different types of orientations (1 - 8 with 1 and 8 included)
    // We limit the number of different tiles to 536870911
    // Otherwise, there is overflow on the hash function
    return (size_t) (obj.rotation + 4 * obj.reflected) * (size_t) 536870911 + (size_t) obj.uid;
  }
};
} // namespace std

#endif // FAST_WFC_UTILS_IDPAIR_HPP_
