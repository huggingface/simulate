// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using System.Collections.Generic;

public class HF_colliders
{
    public List<GLTFCollider> shapes;
    public int? layer;
    public int? mask;
    public bool intangible = false;
}
