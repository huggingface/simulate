// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using Newtonsoft.Json;
using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;


namespace SimEnv.GLTF {
    public class HF_colliders {
        public List<GLTFCollider> colliders;

        public class GLTFCollider{
            public string name = "";
            [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.BOX;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 boundingBox;
            public int? mesh;
            [JsonConverter(typeof(TranslationConverter))] public Vector3 offset = Vector3.zero;
            public bool intangible = false;

            public bool ShouldSerializemesh() { return mesh.HasValue; }
            public bool ShouldSerializeoffset() { return offset != Vector3.zero; }
            public bool ShouldSerializeintangible() { return intangible; }

            // TODO(dylan?) fix this to export the collider at the scene level

            // public static void Export(GLTFNode.ExportResult node) {
            //     Collider[] cols = node.transform.GetComponents<Collider>();
            //     if(cols.Length == 0) {
            //         return;
            //     } else if(cols.Length > 1) {
            //         Debug.LogWarning(string.Format("Node {0} has multiple colliders. Ignoring extras.", node.name));
            //     }
            //     Collider col = cols[0];
            //     HF_colliders collider = new HF_colliders.GLTFCollider();
            //     if(col is BoxCollider) {
            //         collider.type = ColliderType.BOX;
            //         collider.offset = ((BoxCollider)col).center;
            //         collider.boundingBox = ((BoxCollider)col).size;
            //     } else if(col is SphereCollider) {
            //         collider.type = ColliderType.SPHERE;
            //         collider.offset = ((SphereCollider)col).center;
            //         collider.boundingBox = Vector3.one * ((SphereCollider)col).radius;
            //     } else if(col is CapsuleCollider) {
            //         collider.type = ColliderType.CAPSULE;
            //         CapsuleCollider capsule = col as CapsuleCollider;
            //         collider.offset = capsule.center;
            //         collider.boundingBox = new Vector3(capsule.radius, capsule.height, capsule.radius);
            //     } else {
            //         Debug.LogWarning(string.Format("Collider type {0} not implemented", col.GetType()));
            //     }            
            //     if(node.extensions == null)
            //         node.extensions = new GLTFNode.Extensions();
            //     node.extensions.HF_colliders = collider;
            // }
        }
    }
}
