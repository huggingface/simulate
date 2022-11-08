// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using Newtonsoft.Json;
using UnityEngine;
using System.Collections.Generic;

namespace Simulate.GLTF {
    public class HFArticulationBodies {
        public List<GLTFArticulationBody> objects;

        public HFArticulationBodies() {
            objects = new List<GLTFArticulationBody>();
        }

        public class GLTFArticulationBody {
            public string joint_type = "";
            [JsonConverter(typeof(QuaternionConverter))] public Quaternion anchor_rotation = Quaternion.identity;
            [JsonConverter(typeof(TranslationConverter))] public Vector3 anchor_position = Vector3.zero;
            [JsonConverter(typeof(Vector3Converter))] public Vector3? inertia_tensor;
            public bool immovable = false;
            public bool use_gravity = true;
            public float linear_damping = 0.0f;
            public float angular_damping = 0.0f;
            public float joint_friction = 0.0f;
            public float drive_stiffness = 0.0f;
            public float drive_damping = 0.0f;
            public float drive_force_limit = 0.0f;
            public float drive_target = 0.0f;
            public float drive_target_velocity = 0.0f;
            public bool is_limited = false;
            public float upper_limit = 0.0f;
            public float lower_limit = 0.0f;

            public float mass = 1.0f;

            [JsonConverter(typeof(TranslationConverter))] public Vector3 center_of_mass = Vector3.zero;

            // public bool ShouldSerializemesh() { return mesh.HasValue; }
            // public bool ShouldSerializeoffset() { return offset != Vector3.zero; }
            // public bool ShouldSerializeintangible() { return intangible; }

            //     public override int GetHashCode() {
            //         return type.GetHashCode()
            //             ^ boundingBox.GetHashCode()
            //             ^ mesh.GetHashCode()
            //             ^ offset.GetHashCode()
            //             ^ intangible.GetHashCode();
            //     }

            //     public override bool Equals(object obj) {
            //         if (!(obj is GLTFCollider)) return false;
            //         GLTFCollider other = obj as GLTFCollider;
            //         if (type == other.type
            //             && boundingBox == other.boundingBox
            //             && mesh == other.mesh
            //             && offset == other.offset
            //             && intangible == other.intangible)
            //             return true;
            //         return false;
            //     }
        }

        // public static void Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
        //     List<GLTFCollider> objects = new List<GLTFCollider>();
        //     foreach (GLTFNode.ExportResult node in nodes) {
        //         GLTFCollider collider = Export(node);
        //         if (collider == null) continue;
        //         if (!objects.Contains(collider))
        //             objects.Add(collider);
        //         node.extensions ??= new GLTFNode.Extensions();
        //         node.extensions.HF_colliders = new GLTFNode.HFCollider() { object_id = objects.IndexOf(collider) };
        //     }
        //     if (objects.Count == 0) return;
        //     gltfObject.extensions ??= new GLTFExtensions();
        //     gltfObject.extensions.HF_colliders ??= new HFColliders();
        //     gltfObject.extensions.HF_colliders.objects.AddRange(objects);
        //     gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
        // }

        // static GLTFCollider Export(GLTFNode.ExportResult node) {
        //     Collider[] cols = node.transform.GetComponents<Collider>();
        //     if (cols.Length == 0)
        //         return null;
        //     else if (cols.Length > 1)
        //         Debug.LogWarning($"Node {node.name} has multiple colliders. Ignoring extras.");
        //     Collider col = cols[0];
        //     GLTFCollider collider = new GLTFCollider();
        //     if (col is BoxCollider) {
        //         collider.type = ColliderType.box;
        //         collider.offset = ((BoxCollider)col).center;
        //         collider.boundingBox = ((BoxCollider)col).size;
        //     } else if (col is SphereCollider) {
        //         collider.type = ColliderType.sphere;
        //         collider.offset = ((SphereCollider)col).center;
        //         collider.boundingBox = Vector3.one * ((SphereCollider)col).radius;
        //     } else if (col is CapsuleCollider) {
        //         collider.type = ColliderType.capsule;
        //         CapsuleCollider capsule = col as CapsuleCollider;
        //         collider.offset = capsule.center;
        //         collider.boundingBox = new Vector3(capsule.radius, capsule.height, capsule.radius);
        //     } else {
        //         Debug.LogWarning($"Collider type {col.GetType()} not implemented");
        //     }
        //     return collider;
        // }
    }
}
