using UnityEngine;
using SimEnv.GLTF;
using UnityEngine.Rendering.Universal;

namespace SimEnv {
    public class Node : MonoBehaviour {
        public GLTFCamera cameraData;
        public KHRLightsPunctual.GLTFLight lightData;
        public HFColliders.GLTFCollider colliderData;
        public HFRigidbodies.GLTFRigidbody rigidBodyData;
        public HFRlAgents.HFRlAgentsComponent agentData;

        public void Initialize() {
            if (cameraData != null)
                InitializeCamera();
            if (lightData != null)
                InitializeLight();
            if (colliderData != null)
                InitializeCollider();
            if (rigidBodyData != null)
                InitializeRigidBody();
        }

        void InitializeCamera() {
            transform.localRotation *= Quaternion.Euler(0, 180, 0);
            new RenderCamera(this, cameraData);
        }

        void InitializeLight() {
            Light light = gameObject.AddComponent<Light>();
            light.gameObject.AddComponent<UniversalAdditionalLightData>();
            transform.localRotation *= Quaternion.Euler(0, 180, 0);
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
            if (colliderData.mesh.HasValue) {
                Debug.LogWarning("Ignoring collider mesh value");
            }
            if (colliderData.type == ColliderType.BOX) {
                BoxCollider col = gameObject.AddComponent<BoxCollider>();
                col.size = colliderData.boundingBox;
                col.center = colliderData.offset;
                col.isTrigger = colliderData.intangible;
            } else if (colliderData.type == ColliderType.SPHERE) {
                SphereCollider col = gameObject.AddComponent<SphereCollider>();
                col.radius = Mathf.Min(colliderData.boundingBox[0], colliderData.boundingBox[1], colliderData.boundingBox[2]);
                col.center = colliderData.offset;
                col.isTrigger = colliderData.intangible;
            } else if (colliderData.type == ColliderType.CAPSULE) {
                CapsuleCollider col = gameObject.AddComponent<CapsuleCollider>();
                col.radius = Mathf.Min(colliderData.boundingBox[0], colliderData.boundingBox[2]);
                col.height = colliderData.boundingBox[1];
                col.center = colliderData.offset;
                col.isTrigger = colliderData.intangible;
            } else {
                Debug.LogWarning(string.Format("Collider type {0} not implemented", colliderData.GetType()));
            }
        }

        void InitializeRigidBody() {
            Rigidbody rb = gameObject.AddComponent<Rigidbody>();
            rb.mass = rigidBodyData.mass;
            rb.drag = rigidBodyData.drag;
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
        }
    }
}