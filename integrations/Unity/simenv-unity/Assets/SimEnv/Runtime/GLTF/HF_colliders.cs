// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using Newtonsoft.Json;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace SimEnv.GLTF {
    public class HFColliders {
        public List<GLTFCollider> components;

        public HFColliders() {
            components = new List<GLTFCollider>();
        }

        public class GLTFCollider {
            public string name = "";
            [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.box;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 boundingBox;
            public int? mesh;
            [JsonConverter(typeof(TranslationConverter))] public Vector3 offset = Vector3.zero;
            public bool intangible = false;
            public bool convex = false;
            public int? physicMaterial;

            public bool ShouldSerializemesh() { return mesh.HasValue; }
            public bool ShouldSerializeoffset() { return offset != Vector3.zero; }
            public bool ShouldSerializeintangible() { return intangible; }
            public bool ShouldSerializeconvex() { return convex; }

            public override int GetHashCode() {
                return type.GetHashCode()
                    ^ boundingBox.GetHashCode()
                    ^ mesh.GetHashCode()
                    ^ offset.GetHashCode()
                    ^ intangible.GetHashCode()
                    ^ convex.GetHashCode()
                    ^ physicMaterial.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFCollider)) return false;
                GLTFCollider other = obj as GLTFCollider;
                if (type == other.type
                    && boundingBox == other.boundingBox
                    && mesh == other.mesh
                    && offset == other.offset
                    && intangible == other.intangible
                    && convex == other.convex
                    && physicMaterial == other.physicMaterial)
                    return true;
                return false;
            }

            public class ImportResult {
                public GLTFCollider collider;
                public PhysicMaterial physicMaterial;
                public Mesh mesh;
            }
        }

        public class ExportResult : GLTFCollider {
            [JsonIgnore] public GLTFNode.ExportResult node;
            [JsonIgnore] public Collider collider;
        }

        public static List<ExportResult> Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            List<ExportResult> components = new List<ExportResult>();
            foreach (GLTFNode.ExportResult node in nodes) {
                ExportResult collider = Export(node);
                if (collider == null) continue;
                if (!components.Contains(collider))
                    components.Add(collider);
                node.extensions ??= new GLTFNode.Extensions();
                node.extensions.HF_colliders = new GLTFNode.HFCollider() { component_id = components.IndexOf(collider) };
            }
            if (components.Count == 0) return components;
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("HF_colliders");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_colliders ??= new HFColliders();
            gltfObject.extensions.HF_colliders.components.AddRange(components);
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
            return components;
        }

        static ExportResult Export(GLTFNode.ExportResult node) {
            Collider[] cols = node.transform.GetComponents<Collider>();
            if (cols.Length == 0)
                return null;
            else if (cols.Length > 1)
                Debug.LogWarning($"Node {node.name} has multiple colliders. Ignoring extras.");
            Collider col = cols[0];
            ExportResult collider = new ExportResult() {
                node = node,
                collider = col,
            };
            collider.name = col.name;
            if (col is BoxCollider) {
                collider.type = ColliderType.box;
                collider.offset = ((BoxCollider)col).center;
                collider.boundingBox = ((BoxCollider)col).size;
            } else if (col is SphereCollider) {
                collider.type = ColliderType.sphere;
                collider.offset = ((SphereCollider)col).center;
                collider.boundingBox = Vector3.one * ((SphereCollider)col).radius;
            } else if (col is CapsuleCollider) {
                collider.type = ColliderType.capsule;
                CapsuleCollider capsule = col as CapsuleCollider;
                collider.offset = capsule.center;
                collider.boundingBox = new Vector3(capsule.radius, capsule.height, capsule.radius);
            } else if (col is MeshCollider) {
                collider.type = ColliderType.mesh;
                MeshCollider meshCollider = col as MeshCollider;
                collider.mesh = node.colliderMesh;
                collider.convex = meshCollider.convex;
            } else {
                Debug.LogWarning($"Collider type {col.GetType()} not implemented");
            }
            return collider;
        }
    }
}
