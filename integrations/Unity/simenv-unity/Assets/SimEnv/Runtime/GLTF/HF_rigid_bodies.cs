using Newtonsoft.Json;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;


namespace SimEnv.GLTF {
    public class HFRigidBodies {
        public List<GLTFRigidBody> rigidbodies;

        public HFRigidBodies() {
            rigidbodies = new List<GLTFRigidBody>();
        }

        public class GLTFRigidBody {
            [JsonProperty(Required = Required.Always)] public float mass;
            public float drag = 0f;
            public float angular_drag = 0f;
            [JsonProperty(Required = Required.Always)] public List<string> constraints = new List<string>();
            public string name = "";
            public bool use_gravity = true;
            public bool continuous = false;
            public bool kinematic = false;

            public bool ShouldSerializedrag() => drag != 0f;
            public bool ShouldSerializeangular_drag() => angular_drag != 0f;
            public bool ShouldSerializeuse_gravity() => !use_gravity;
            public bool ShouldSerializecontinuous() => continuous;
            public bool ShouldSerializekinematic() => kinematic;
        }

        public static void Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            List<GLTFRigidBody> rigidbodies = new List<GLTFRigidBody>();
            foreach (GLTFNode.ExportResult node in nodes) {
                GLTFRigidBody rigidbody = Export(node);
                if (rigidbody == null) continue;
                if (!rigidbodies.Contains(rigidbody))
                    rigidbodies.Add(rigidbody);
                node.extensions ??= new GLTFNode.Extensions();
                node.extensions.HF_rigidbodies = new GLTFNode.HFRigidbody() { rigidbody = rigidbodies.IndexOf(rigidbody) };
            }
            if (rigidbodies.Count == 0) return;
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_rigidbodies ??= new HFRigidBodies();
            gltfObject.extensions.HF_rigidbodies.rigidbodies.AddRange(rigidbodies);
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
        }

        static GLTFRigidBody Export(GLTFNode.ExportResult node) {
            Rigidbody[] rigidbodies = node.transform.GetComponents<Rigidbody>();
            if (rigidbodies.Length == 0)
                return null;
            else if (rigidbodies.Length > 1)
                Debug.LogWarning($"Node {node.name} has multiple rigidbodies. Ignoring extras.");
            Rigidbody rigidbody = rigidbodies[0];
            GLTFRigidBody gltfRigidbody = new GLTFRigidBody();
            gltfRigidbody.mass = rigidbody.mass;
            gltfRigidbody.linear_drag = rigidbody.linear_drag;
            gltfRigidbody.angular_drag = rigidbody.angularDrag;
            gltfRigidbody.constraints = new List<string>();
            if ((rigidbody.constraints & RigidbodyConstraints.FreezePositionX) == RigidbodyConstraints.FreezePositionX)
                gltfRigidbody.constraints.Add("freeze_position_x");
            if ((rigidbody.constraints & RigidbodyConstraints.FreezePositionY) == RigidbodyConstraints.FreezePositionY)
                gltfRigidbody.constraints.Add("freeze_position_y");
            if ((rigidbody.constraints & RigidbodyConstraints.FreezePositionZ) == RigidbodyConstraints.FreezePositionZ)
                gltfRigidbody.constraints.Add("freeze_position_z");
            if ((rigidbody.constraints & RigidbodyConstraints.FreezeRotationX) == RigidbodyConstraints.FreezeRotationX)
                gltfRigidbody.constraints.Add("freeze_rotation_x");
            if ((rigidbody.constraints & RigidbodyConstraints.FreezeRotationY) == RigidbodyConstraints.FreezeRotationY)
                gltfRigidbody.constraints.Add("freeze_rotation_y");
            if ((rigidbody.constraints & RigidbodyConstraints.FreezeRotationZ) == RigidbodyConstraints.FreezeRotationZ)
                gltfRigidbody.constraints.Add("freeze_rotation_z");
            gltfRigidbody.name = rigidbody.name;
            gltfRigidbody.use_gravity = rigidbody.useGravity;
            gltfRigidbody.kinematic = rigidbody.isKinematic;
            gltfRigidbody.continuous = rigidbody.collisionDetectionMode != CollisionDetectionMode.Discrete;
            return gltfRigidbody;
        }
    }
}
