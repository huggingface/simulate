extends Node
class_name GLTFEnums


enum AlphaMode { OPAQUE, MASK, BLEND }
enum AccessorType { SCALAR, VEC2, VEC3, VEC4, MAT2, MAT3, MAT4 }
enum RenderingMode { POINTS, LINES, LINE_LOOP, LINE_STRIP, TRIANGLES, TRIANGLE_STRIP, TRIANGLE_FAN }
enum GLType { UNSET = -1, BYTE = 5120, UNSIGNED_BYTE = 5121, SHORT = 5122, UNSIGNED_SHORT = 5123, UNSIGNED_INT = 5125, FLOAT = 5126 }
enum Format { AUTO, GLTF, GLB }
enum CameraType { perspective, orthographic }
enum LightType { directional, point, spot }
enum ColliderType { box, sphere, capsule, mesh }
enum InterpolationMode { ImportFromFile = -1, LINEAR = 0, STEP = 1, CUBICSPLINE = 2 }
