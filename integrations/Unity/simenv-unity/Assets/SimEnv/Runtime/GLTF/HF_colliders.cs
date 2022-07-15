// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using Newtonsoft.Json;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace SimEnv.GLTF {
    public class HFColliders {
        public List<GLTFCollider> colliders;

        public HFColliders() {
            colliders = new List<GLTFCollider>();
        }

        public class GLTFCollider {
            public string name = "";
            [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.BOX;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 boundingBox;
            public int? mesh;
            [JsonConverter(typeof(TranslationConverter))] public Vector3 offset = Vector3.zero;
            public bool intangible = false;

            public bool ShouldSerializemesh() { return mesh.HasValue; }
            public bool ShouldSerializeoffset() { return offset != Vector3.zero; }
            public bool ShouldSerializeintangible() { return intangible; }

            public override int GetHashCode() {
                return type.GetHashCode()
                    ^ boundingBox.GetHashCode()
                    ^ mesh.GetHashCode()
                    ^ offset.GetHashCode()
                    ^ intangible.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFCollider)) return false;
                GLTFCollider other = obj as GLTFCollider;
                if (type == other.type
                    && boundingBox == other.boundingBox
                    && mesh == other.mesh
                    && offset == other.offset
                    && intangible == other.intangible)
                    return true;
                return false;
            }
        }

        public static void Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            List<GLTFCollider> colliders = new List<GLTFCollider>();
            foreach (GLTFNode.ExportResult node in nodes) {
                GLTFCollider collider = Export(node);
                if (collider == null) continue;
                if (!colliders.Contains(collider))
                    colliders.Add(collider);
                node.extensions ??= new GLTFNode.Extensions();
                node.extensions.HF_colliders = new GLTFNode.HFCollider() { collider = colliders.IndexOf(collider) };
            }
            if (colliders.Count == 0) return;
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_colliders ??= new HFColliders();
            gltfObject.extensions.HF_colliders.colliders.AddRange(colliders);
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
        }

        static GLTFCollider Export(GLTFNode.ExportResult node) {
            Collider[] cols = node.transform.GetComponents<Collider>();
            if (cols.Length == 0)
                return null;
            else if (cols.Length > 1)
                Debug.LogWarning($"Node {node.name} has multiple colliders. Ignoring extras.");
            Collider col = cols[0];
            GLTFCollider collider = new GLTFCollider();
            if (col is BoxCollider) {
                collider.type = ColliderType.BOX;
                collider.offset = ((BoxCollider)col).center;
                collider.boundingBox = ((BoxCollider)col).size;
            } else if (col is SphereCollider) {
                collider.type = ColliderType.SPHERE;
                collider.offset = ((SphereCollider)col).center;
                collider.boundingBox = Vector3.one * ((SphereCollider)col).radius;
            } else if (col is CapsuleCollider) {
                collider.type = ColliderType.CAPSULE;
                CapsuleCollider capsule = col as CapsuleCollider;
                collider.offset = capsule.center;
                collider.boundingBox = new Vector3(capsule.radius, capsule.height, capsule.radius);
            } else {
                Debug.LogWarning($"Collider type {col.GetType()} not implemented");
            }
            return collider;
        }
    }
}
