// based on https://github.com/Moguri/glTF/tree/panda3d_physics_collision_shapes/extensions/2.0/Vendor/PANDA3D_collision_shapes
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HF_colliders {
        [JsonProperty(Required = Required.Always)] public List<ColliderShape> shapes;
        // TODO: implement node layers, and mask as global extension (which layers collide with which)

        public class ColliderShape {
            [JsonConverter(typeof(EnumConverter))] public ColliderType type = ColliderType.BOX;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 boundingBox;
            public string primaryAxis = "Y";
            public int? mesh;
            [JsonConverter(typeof(Matrix4x4Converter))] public Matrix4x4 offsetMatrix = Matrix4x4.identity;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 offsetTranslation = Vector3.zero;
            [JsonConverter(typeof(QuaternionConverter))] public Quaternion offsetRotation = Quaternion.identity;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 offsetScale = Vector3.one;
            public bool intangible = false;

            public bool ShouldSerializeprimaryAxis() { return primaryAxis != "Y"; }
            public bool ShouldSerializemesh() { return mesh.HasValue; }
            public bool ShouldSerializeoffsetMatrix() { return offsetMatrix != Matrix4x4.identity; }
            public bool ShouldSerializeoffsetTranslation() { return offsetTranslation != Vector3.zero; }
            public bool ShouldSerializeoffsetRotation() { return offsetRotation != Quaternion.identity; }
            public bool ShouldSerializeoffsetScale() { return offsetScale != Vector3.one; }
            public bool ShouldSerializeintangible() { return intangible; }
        }

        public static void Export(List<GLTFNode.ExportResult> nodes) {
            foreach(GLTFNode.ExportResult node in nodes)
                Export(node);
        }

        static void Export(GLTFNode.ExportResult node) {
            Collider[] colliders = node.transform.GetComponents<Collider>();
            if(colliders.Length > 0) {
                List<HF_colliders.ColliderShape> shapes = new List<HF_colliders.ColliderShape>();
                foreach(Collider collider in colliders) {
                    HF_colliders.ColliderShape shape = new HF_colliders.ColliderShape();
                    if(collider is BoxCollider) {
                        shape.type = ColliderType.BOX;
                        shape.offsetTranslation = ((BoxCollider)collider).center;
                        shape.boundingBox = ((BoxCollider)collider).size;
                    } else if(collider is SphereCollider) {
                        shape.type = ColliderType.SPHERE;
                        shape.offsetTranslation = ((SphereCollider)collider).center;
                        shape.boundingBox = Vector3.one * ((SphereCollider)collider).radius;
                    } else if(collider is CapsuleCollider) {
                        shape.type = ColliderType.CAPSULE;
                        CapsuleCollider capsule = collider as CapsuleCollider;
                        shape.offsetTranslation = capsule.center;
                        shape.boundingBox = new Vector3(capsule.radius, capsule.height, capsule.radius);
                    } else {
                        Debug.LogWarning(string.Format("Collider type {0} not implemented", collider.GetType()));
                    }
                    shapes.Add(shape);
                }
                HF_colliders hf_colliders = new HF_colliders() { 
                    shapes = shapes
                };
                if(node.extensions == null)
                    node.extensions = new GLTFNode.Extensions();
                node.extensions.HF_colliders = hf_colliders;
            }
        }
    }
}
