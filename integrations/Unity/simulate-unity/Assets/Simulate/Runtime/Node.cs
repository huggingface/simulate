using UnityEngine;
using Simulate.GLTF;
using UnityEngine.Rendering.Universal;
using Newtonsoft.Json;
using System.Collections.Generic;
namespace Simulate {
    public class Node : MonoBehaviour {
        public GLTFCamera cameraData;
        public KHRLightsPunctual.GLTFLight lightData;
        public HFColliders.GLTFCollider.ImportResult colliderData;
        public HFRigidBodies.GLTFRigidBody rigidBodyData;
        public HFArticulationBodies.GLTFArticulationBody articulationBodyData;
        public HFActuators.HFActuator actuatorData;
        public HFStateSensors.HFStateSensor stateSensorData;
        public HFRaycastSensors.HFRaycastSensor raycastSensorData;
        public HFRewardFunctions.HFRewardFunction rewardFunctionData;
        public new RenderCamera camera { get; private set; }
        public new Light light { get; private set; }
        public new Collider collider { get; private set; }
        public new Rigidbody rigidbody { get; private set; }
        public ArticulationBody articulationBody { get; private set; }
        public HFActuators.Actuator actuator { get; private set; }
        public Data initialState { get; private set; }
        public bool isActor { get; set; }

        public void Initialize() {
            if (cameraData != null)
                InitializeCamera();
            if (lightData != null)
                InitializeLight();
            if (colliderData != null)
                InitializeCollider();
            if (rigidBodyData != null)
                InitializeRigidBody();
            if (articulationBodyData != null)
                InitializeArticulationBody();
            if (actuatorData != null)
                InitializeActuator();
            initialState = GetData();
        }
        public void ResetState(Vector3 offset = default(Vector3)) {
            if (articulationBody == null) {
                // you cannot teleport articulation bodies so simply (see below)
                transform.position = offset + initialState.position;
                transform.rotation = initialState.rotation;
            }
            if (rigidbody != null) {
                rigidbody.velocity = Vector3.zero;
                rigidbody.angularVelocity = Vector3.zero;
            }

            if (articulationBody != null) {
                // https://forum.unity.com/threads/reset-pos-rot-of-articulation-bodies-manually-without-a-cacophony-of-derp.958741/
                // see http://anja-haumann.de/unity-preserve-articulation-body-state/ a great resource
                articulationBody.velocity = Vector3.zero;
                articulationBody.angularVelocity = Vector3.zero;

                articulationBody.jointPosition = new ArticulationReducedSpace(0f, 0f, 0f);
                articulationBody.jointAcceleration = new ArticulationReducedSpace(0f, 0f, 0f);
                articulationBody.jointForce = new ArticulationReducedSpace(0f, 0f, 0f);
                articulationBody.jointVelocity = new ArticulationReducedSpace(0f, 0f, 0f);

                var drive = articulationBody.xDrive;
                drive.target = 0f;
                articulationBody.xDrive = drive;

                if (articulationBody.isRoot) {
                    // this is the only way we can adjust the position of an articulation body
                    articulationBody.TeleportRoot(initialState.position + offset, initialState.rotation);
                }
            }
        }

        void InitializeActuator() {
            actuator = new HFActuators.Actuator(actuatorData);
        }

        void InitializeCamera() {
            camera = new RenderCamera(this, cameraData);
        }

        /* void InitializeStateSensor() {
            sensor = new StateSensor(this, stateSensorData);
        }
        void InitializeRaycastSensor() {
            sensor = new RaycastSensor(this, raycastSensorData);
        } */

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
            Collider sharedCollider = null;
            if (collider.type == ColliderType.box) {
                BoxCollider col = gameObject.AddComponent<BoxCollider>();
                col.size = collider.bounding_box;
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
                sharedCollider = col;
            } else if (collider.type == ColliderType.sphere) {
                SphereCollider col = gameObject.AddComponent<SphereCollider>();
                col.radius = Mathf.Min(collider.bounding_box[0], collider.bounding_box[1], collider.bounding_box[2]);
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
                sharedCollider = col;
            } else if (collider.type == ColliderType.capsule) {
                CapsuleCollider col = gameObject.AddComponent<CapsuleCollider>();
                col.radius = Mathf.Min(collider.bounding_box[0], collider.bounding_box[2]);
                col.height = collider.bounding_box[1];
                col.center = collider.offset;
                col.isTrigger = collider.intangible;
                this.collider = col;
                sharedCollider = col;
            } else if (collider.type == ColliderType.mesh) {
                MeshCollider col = gameObject.AddComponent<MeshCollider>();
                col.sharedMesh = colliderData.mesh;
                col.isTrigger = collider.intangible;
                col.convex = collider.convex;
                this.collider = col;
                sharedCollider = col;
            } else {
                Debug.LogWarning(string.Format("Collider type {0} not implemented", collider.GetType()));
                return;
            }
            if (colliderData.physicMaterial != null)
                sharedCollider.sharedMaterial = colliderData.physicMaterial;
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

        void InitializeArticulationBody() {
            ArticulationBody ab = gameObject.AddComponent<ArticulationBody>();
            switch (articulationBodyData.joint_type) {
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
                    Debug.LogWarning(string.Format("Joint type {0} not implemented", articulationBodyData.joint_type));
                    break;
            }

            ab.anchorPosition = articulationBodyData.anchor_position;
            ab.anchorRotation = articulationBodyData.anchor_rotation;

            // we should only try and set this property if we are the root in a chain of articulated bodies
            if (articulationBodyData.immovable){
                ab.immovable = articulationBodyData.immovable;
            }
            // this property should likely be consistent across all bodies in the chain, or just locked to a base node
            ab.useGravity = articulationBodyData.use_gravity;

            // setting match anchors to false ensures we can deactivate and activate the articulation body
            // see http://anja-haumann.de/unity-preserve-articulation-body-state/
            ab.matchAnchors = false;
            ab.linearDamping = articulationBodyData.linear_damping;
            ab.angularDamping = articulationBodyData.angular_damping;
            ab.jointFriction = articulationBodyData.joint_friction;
            ab.mass = articulationBodyData.mass;
            ab.centerOfMass = articulationBodyData.center_of_mass;
            if (articulationBodyData.inertia_tensor != null) {
                ab.inertiaTensor = articulationBodyData.inertia_tensor.Value;
            }
            if (articulationBodyData.is_limited){
                ab.twistLock = ArticulationDofLock.LimitedMotion;   // for revolute joints
                ab.linearLockX = ArticulationDofLock.LimitedMotion; // for prismatic joints
            }
            ArticulationDrive xDrive = new ArticulationDrive() {
                stiffness = articulationBodyData.drive_stiffness,
                forceLimit = articulationBodyData.drive_force_limit,
                damping = articulationBodyData.drive_damping,
                lowerLimit = articulationBodyData.lower_limit,
                upperLimit = articulationBodyData.upper_limit
            };
            ab.xDrive = xDrive;
            articulationBody = ab;
        }

        public Data GetData() {
            Vector3? velocity = null;
            Vector3? angularVelocity = null;
            Rigidbody rb = gameObject.GetComponent<Rigidbody>();
            if (rb != null) {
                velocity = rb.velocity;
                angularVelocity = rb.angularVelocity;
            } else {
                ArticulationBody ab = gameObject.GetComponent<ArticulationBody>();
                if (ab != null) {
                    velocity = ab.velocity;
                    angularVelocity = ab.angularVelocity;
                }
            }

            return new Data() {
                name = gameObject.name,
                position = transform.position,
                rotation = transform.rotation,
                velocity = velocity,
                angular_velocity = angularVelocity
            };
        }

        public class Data {
            public string name;
            [JsonConverter(typeof(Vector3Converter))] public Vector3 position;
            [JsonConverter(typeof(QuaternionConverter))] public Quaternion rotation;
            [JsonConverter(typeof(Vector3Converter))] public Vector3? velocity;
            [JsonConverter(typeof(Vector3Converter))] public Vector3? angular_velocity;
        }
    }
}