using UnityEngine;
using SimEnv.GLTF;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;

namespace SimEnv {
    public class Node : MonoBehaviour {
        public GLTFCamera cameraData;
        public KHRLightsPunctual.GLTFLight lightData;
        public HFColliders.GLTFCollider.ImportResult colliderData;
        public HFRigidBodies.GLTFRigidBody rigidBodyData;
        public HFArticulatedBodies.GLTFArticulatedBody articulatedBodyData;
        public HFRlAgents.HFRlAgentsComponent agentData;

        public new RenderCamera camera { get; private set; }
        public new Light light { get; private set; }
        public new Collider collider { get; private set; }
        public new Rigidbody rigidbody { get; private set; }
        public ArticulationBody articulatedBody { get; private set; }

        public Data initialState { get; private set; }

        public void Initialize() {
            if (cameraData != null)
                InitializeCamera();
            if (lightData != null)
                InitializeLight();
            if (colliderData != null)
                InitializeCollider();
            if (rigidBodyData != null)
                InitializeRigidBody();
            if (articulatedBodyData != null)
                InitializeArticulatedBody();
            initialState = GetData();
        }

        public void ResetState() {
            transform.position = new Vector3(
                initialState.position[0],
                initialState.position[1],
                initialState.position[2]
            );
            transform.rotation = new Quaternion(
                initialState.rotation[0],
                initialState.rotation[1],
                initialState.rotation[2],
                initialState.rotation[3]
            );
        }

        void InitializeCamera() {
            camera = new RenderCamera(this, cameraData);
        }

        void InitializeLight() {
            light = gameObject.AddComponent<Light>();
            light.gameObject.AddComponent<UniversalAdditionalLightData>();
            gameObject.transform.localRotation *= Quaternion.Euler(0, 180, 0);
            if (!string.IsNullOrEmpty(lightData.name))
                light.transform.gameObject.name = lightData.name;
            light.color = lightData.color;
            light.intensity = lightData.intensity;
            light.range = lightData.range;
            light.shadows = LightShadows.Soft;
            switch (lightData.type) {
                case GLTF.LightType.directional:
                    light.type = UnityEngine.LightType.Directional;
                    break;
                case GLTF.LightType.point:
                    light.type = UnityEngine.LightType.Point;
                    break;
                case GLTF.LightType.spot:
                    light.type = UnityEngine.LightType.Spot;
                    break;
            }
        }

        void InitializeCollider() {
            HFColliders.GLTFCollider collider = colliderData.collider;
            if (collider.type == ColliderType.box) {
                BoxCollider col = gameObject.AddComponent<BoxCollider>();
                col.size = collider.boundingBox;
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
            } else if (collider.type == ColliderType.sphere) {
                SphereCollider col = gameObject.AddComponent<SphereCollider>();
                col.radius = Mathf.Min(collider.boundingBox[0], collider.boundingBox[1], collider.boundingBox[2]);
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
            } else if (collider.type == ColliderType.capsule) {
                CapsuleCollider col = gameObject.AddComponent<CapsuleCollider>();
                col.radius = Mathf.Min(collider.boundingBox[0], collider.boundingBox[2]);
                col.height = collider.boundingBox[1];
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
            } else if (collider.type == ColliderType.mesh) {
                MeshCollider col = gameObject.AddComponent<MeshCollider>();
                col.sharedMesh = colliderData.mesh;
                col.isTrigger = collider.intangible;
                col.convex = collider.convex;
                this.collider = col;
            } else {
                Debug.LogWarning(string.Format("Collider type {0} not implemented", collider.GetType()));
            }
        }

        void InitializeRigidBody() {
            Rigidbody rb = gameObject.AddComponent<Rigidbody>();
            rb.mass = rigidBodyData.mass;
            rb.drag = rigidBodyData.linear_drag;
            rb.angularDrag = rigidBodyData.angular_drag;
            rb.useGravity = rigidBodyData.use_gravity;
            rb.collisionDetectionMode = rigidBodyData.continuous ? CollisionDetectionMode.Continuous : CollisionDetectionMode.Discrete;
            rb.isKinematic = rigidBodyData.kinematic;

            foreach (string constraint in rigidBodyData.constraints) {
                switch (constraint) {
                    case "freeze_position_x":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezePositionX;
                        break;
                    case "freeze_position_y":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezePositionY;
                        break;
                    case "freeze_position_z":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezePositionZ;
                        break;
                    case "freeze_rotation_x":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezeRotationX;
                        break;
                    case "freeze_rotation_y":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezeRotationY;
                        break;
                    case "freeze_rotation_z":
                        rb.constraints = rb.constraints | RigidbodyConstraints.FreezeRotationZ;
                        break;
                    default:
                        Debug.LogWarning(string.Format("Constraint {0} not implemented", constraint));
                        break;
                }
            }

            rigidbody = rb;
        }

        void InitializeArticulatedBody() {
            ArticulationBody ab = gameObject.AddComponent<ArticulationBody>();
            switch (articulatedBodyData.joint_type) {
                case "fixed":
                    ab.jointType = ArticulationJointType.FixedJoint;
                    break;
                case "prismatic":
                    ab.jointType = ArticulationJointType.PrismaticJoint;
                    break;
                case "revolute":
                    ab.jointType = ArticulationJointType.RevoluteJoint;
                    break;
                default:
                    Debug.LogWarning(string.Format("Joint type {0} not implemented", articulatedBodyData.joint_type));
                    break;
            }
            ab.anchorPosition = articulatedBodyData.anchor_position;
            ab.anchorRotation = articulatedBodyData.anchor_rotation;
            ab.linearDamping = articulatedBodyData.linear_damping;
            ab.angularDamping = articulatedBodyData.angular_damping;
            ab.jointFriction = articulatedBodyData.joint_friction;
            ab.mass = articulatedBodyData.mass;
            ab.centerOfMass = articulatedBodyData.center_of_mass;
            if (articulatedBodyData.inertia_tensor != null) {
                ab.inertiaTensor = articulatedBodyData.inertia_tensor.Value;
            }

            ArticulationDrive xDrive = new ArticulationDrive() {
                stiffness = articulatedBodyData.drive_stifness,
                forceLimit = articulatedBodyData.drive_force_limit,
                damping = articulatedBodyData.drive_damping,
                lowerLimit = articulatedBodyData.lower_limit,
                upperLimit = articulatedBodyData.upper_limit
            };
            ab.xDrive = xDrive;
            articulatedBody = ab;
        }

        public Data GetData() {
            return new Data() {
                name = gameObject.name,
                position = transform.position,
                rotation = transform.rotation,
            };
        }

        public class Data {
            public string name;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 position;
            [JsonConverter(typeof(QuaternionConverter))] public Quaternion rotation;
        }
    }
}