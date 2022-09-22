// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using Newtonsoft.Json;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace Simulate.GLTF {
    public class HFColliders {
        public List<GLTFCollider> objects;

        public HFColliders() {
            objects = new List<GLTFCollider>();
        }

        public class GLTFCollider {
            public string name = "";
            [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.box;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 bounding_box;
            [JsonConverter(typeof(TranslationConverter))] public Vector3 offset = Vector3.zero;
            public bool intangible = false;
            public bool convex = false;
            public int? physic_material;

            public bool ShouldSerializebounding_box() => bounding_box != Vector3.zero;
            public bool ShouldSerializeoffset() => offset != Vector3.zero;
            public bool ShouldSerializeintangible() => intangible;
            public bool ShouldSerializeconvex() => convex;

            public override int GetHashCode() {
                return type.GetHashCode()
                    ^ bounding_box.GetHashCode()
                    ^ offset.GetHashCode()
                    ^ intangible.GetHashCode()
                    ^ convex.GetHashCode()
                    ^ physic_material.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFCollider)) return false;
                GLTFCollider other = obj as GLTFCollider;
                if (type == other.type
                    && bounding_box == other.bounding_box
                    && offset == other.offset
                    && intangible == other.intangible
                    && convex == other.convex
                    && physic_material == other.physic_material)
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
            List<ExportResult> objects = new List<ExportResult>();
            foreach (GLTFNode.ExportResult node in nodes) {
                ExportResult collider = Export(node);
                if (collider == null) continue;
                if (!objects.Contains(collider))
                    objects.Add(collider);
                node.extensions ??= new GLTFNode.Extensions();
                node.extensions.HF_colliders = new GLTFNode.NodeExtension() { 
                    name = collider.name,
                    object_id = objects.IndexOf(collider),
                };
            }
            if (objects.Count == 0) return objects;
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("HF_colliders");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_colliders ??= new HFColliders();
            gltfObject.extensions.HF_colliders.objects.AddRange(objects);
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
            return objects;
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
                intangible = col.isTrigger,
            };
            collider.name = col.name;
            if (col is BoxCollider) {
                collider.type = ColliderType.box;
                collider.offset = ((BoxCollider)col).center;
                collider.bounding_box = ((BoxCollider)col).size;
            } else if (col is SphereCollider) {
                collider.type = ColliderType.sphere;
                collider.offset = ((SphereCollider)col).center;
                collider.bounding_box = Vector3.one * ((SphereCollider)col).radius;
            } else if (col is CapsuleCollider) {
                collider.type = ColliderType.capsule;
                CapsuleCollider capsule = col as CapsuleCollider;
                collider.offset = capsule.center;
                collider.bounding_box = new Vector3(capsule.radius, capsule.height, capsule.radius);
            } else if (col is MeshCollider) {
                collider.type = ColliderType.mesh;
                MeshCollider meshCollider = col as MeshCollider;
                collider.convex = meshCollider.convex;
            } else {
                Debug.LogWarning($"Collider type {col.GetType()} not implemented");
            }
            return collider;
        }
    }
}
