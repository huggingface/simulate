// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFNode.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System;
using System.Linq;
using SimEnv.RlAgents;
using UnityEngine.Rendering.Universal;

namespace SimEnv.GLTF {
    public class GLTFNode {
        public string name;
        public int[] children;
        [JsonConverter(typeof(Matrix4x4Converter))] public Matrix4x4 matrix = Matrix4x4.identity;
        [JsonConverter(typeof(TranslationConverter))] public Vector3 translation = Vector3.zero;
        [JsonConverter(typeof(QuaternionConverter))] public Quaternion rotation = Quaternion.identity;
        [JsonConverter(typeof(Vector3Converter))] public Vector3 scale = Vector3.one;
        public int? mesh;
        public int? skin;
        public int? camera;
        public int? weights;
        public Extensions extensions;

        public bool ShouldSerializematrix() { return matrix != Matrix4x4.identity; }
        public bool ShouldSerializetranslation() { return translation != Vector3.zero; }
        public bool ShouldSerializerotation() { return rotation != Quaternion.identity; }
        public bool ShouldSerializescale() { return scale != Vector3.one; }

        public class Extensions {
            public KHRLight KHR_lights_punctual;
            public HFCollider HF_colliders;
            public HFArticulatedBody HF_articulated_bodies;
            public HFRlAgent HF_rl_agents;
            public HFRigidbody HF_rigid_bodies;
            public HFCameraSensor HF_camera_sensors;
            public HFStateSensor HF_state_sensors;
            public string[] HF_custom;
        }

        [Serializable]
        public class CustomExtensionWrapper {
            public string type;
            public string contents;
        }

        public class HFRlAgent {
            public int agent;
        }
        public class HFCameraSensor {
            public int camera_sensor;
        }
        public class HFStateSensor {
            public int state_sensor;
        }

        public class HFRigidbody {
            public int component_id;
        }

        public class KHRLight {
            public int light;
        }

        public class HFCollider {
            public int component_id;
        }

        public class HFArticulatedBody {
            public int component_id;
        }

        public class ImportResult {
            public int? parent;
            public int[] children;
            public Transform transform;
            public Node node;

            public bool IsRoot => !parent.HasValue;
        }

        public void ApplyMatrix(Transform transform) {
            if (matrix != Matrix4x4.identity)
                matrix.UnpackMatrix(ref translation, ref rotation, ref scale);
            transform.localPosition = translation;
            transform.localRotation = rotation;
            transform.localScale = scale;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            List<GLTFNode> nodes;
            GLTFMesh.ImportTask meshTask;
            GLTFSkin.ImportTask skinTask;
            List<GLTFCamera> cameras;
            GLTFExtensions extensions;

            public ImportTask(List<GLTFNode> nodes, GLTFMesh.ImportTask meshTask, GLTFSkin.ImportTask skinTask, List<GLTFCamera> cameras, GLTFExtensions extensions) : base(meshTask, skinTask) {
                this.nodes = nodes;
                this.meshTask = meshTask;
                this.skinTask = skinTask;
                this.cameras = cameras;
                this.extensions = extensions;
            }

            public override IEnumerator TaskCoroutine(Action<float> onProgress = null) {
                if (nodes == null) {
                    if (onProgress != null)
                        onProgress(1f);
                    IsCompleted = true;
                    yield break;
                }

                // Create gameObjects - give names and register Nodes with the Simulator
                result = new ImportResult[nodes.Count];
                for (int i = 0; i < result.Length; i++) {
                    result[i] = new GLTFNode.ImportResult();
                    result[i].transform = new GameObject().transform;
                    result[i].transform.gameObject.name = nodes[i].name;
                    result[i].node = result[i].transform.gameObject.AddComponent<Node>();
                    if (Application.isPlaying)
                        result[i].node.Initialize();
                }

                // Connect children and parents in our gameObjects transforms
                for (int i = 0; i < result.Length; i++) {
                    if (nodes[i].children != null) {
                        int[] children = nodes[i].children;
                        result[i].children = children;
                        for (int k = 0; k < children.Length; k++) {
                            int childIndex = children[k];
                            result[childIndex].parent = i;
                            result[childIndex].transform.parent = result[i].transform;
                        }
                    }
                }

                // Set position, rotation, scale
                for (int i = 0; i < result.Length; i++)
                    nodes[i].ApplyMatrix(result[i].transform);

                // Now we add the more complex properties to the nodes (Mesh, Lights, Colliders, Cameras, RL Agents, etc)
                // Mesh
                for (int i = 0; i < result.Length; i++) {
                    if (nodes[i].mesh.HasValue) {
                        GLTFMesh.ImportResult meshResult = meshTask.result[nodes[i].mesh.Value];
                        if (meshResult == null) continue;

                        Mesh mesh = meshResult.mesh;
                        Renderer renderer;
                        if (nodes[i].skin.HasValue) {
                            GLTFSkin.ImportResult skin = skinTask.result[nodes[i].skin.Value];
                            renderer = skin.SetupSkinnedMeshRenderer(result[i].transform.gameObject, mesh, result);
                        } else if (mesh.blendShapeCount > 0) {
                            SkinnedMeshRenderer skinnedMeshRenderer = result[i].transform.gameObject.AddComponent<SkinnedMeshRenderer>();
                            skinnedMeshRenderer.sharedMesh = mesh;
                            renderer = skinnedMeshRenderer;
                        } else {
                            MeshRenderer meshRenderer = result[i].transform.gameObject.AddComponent<MeshRenderer>();
                            MeshFilter meshFilter = result[i].transform.gameObject.AddComponent<MeshFilter>();
                            meshFilter.sharedMesh = mesh;
                            renderer = meshRenderer;
                        }
                        renderer.materials = meshResult.materials;
                        if (string.IsNullOrEmpty(result[i].transform.name))
                            result[i].transform.name = "node" + i;
                    } else {
                        if (string.IsNullOrEmpty(result[i].transform.name))
                            result[i].transform.name = "node" + i;
                    }

                    // Camera
                    if (nodes[i].camera.HasValue) {
                        GLTFCamera cameraData = cameras[nodes[i].camera.Value];
                        Camera camera = result[i].transform.gameObject.AddComponent<Camera>();
                        result[i].transform.localRotation *= Quaternion.Euler(0, 180, 0);
                        switch (cameraData.type) {
                            case CameraType.orthographic:
                                camera.orthographic = true;
                                camera.nearClipPlane = cameraData.orthographic.znear;
                                camera.farClipPlane = cameraData.orthographic.zfar;
                                camera.orthographicSize = cameraData.orthographic.ymag;
                                break;
                            case CameraType.perspective:
                                camera.orthographic = false;
                                camera.nearClipPlane = cameraData.perspective.znear;
                                if (cameraData.perspective.zfar.HasValue)
                                    camera.farClipPlane = cameraData.perspective.zfar.Value;
                                if (cameraData.perspective.aspectRatio.HasValue)
                                    camera.aspect = cameraData.perspective.aspectRatio.Value;
                                camera.fieldOfView = Mathf.Rad2Deg * cameraData.perspective.yfov;
                                break;
                        }
                    }

                    // Extensions (lights, colliders, sensors, RL agents, etc)
                    if (nodes[i].extensions != null) {

                        // RL Agents
                        if (nodes[i].extensions.HF_rl_agents != null) {
                            int agentValue = nodes[i].extensions.HF_rl_agents.agent;
                            if (extensions == null || extensions.HF_rl_agents == null || extensions.HF_rl_agents.agents == null || extensions.HF_rl_agents.agents.Count < agentValue) {
                                Debug.LogWarning("Error importing agent");
                            } else {
                                HFRlAgents.HFRlAgentsComponent agentData = extensions.HF_rl_agents.agents[agentValue];
                                Agent agent = new Agent(result[i].node, agentData);
                            }
                        }

                        // Sensors
                        // Camera Sensor
                        if (nodes[i].extensions.HF_camera_sensors != null) {

                            int sensorValue = nodes[i].extensions.HF_camera_sensors.camera_sensor;
                            if (extensions == null || extensions.HF_camera_sensors == null || extensions.HF_camera_sensors.camera_sensors == null || extensions.HF_camera_sensors.camera_sensors.Count < sensorValue) {
                                Debug.LogWarning("Error importing camera sensor");
                            } else {
                                Debug.Log("Loading camera " + extensions.HF_camera_sensors.camera_sensors.Count.ToString());
                                HFCameraSensors.HFCameraSensor cameraData = extensions.HF_camera_sensors.camera_sensors[sensorValue];

                                CameraSensor camera = new CameraSensor(result[i].node, cameraData);
                            }
                        }
                        // State Sensor
                        if (nodes[i].extensions.HF_state_sensors != null) {

                            int sensorValue = nodes[i].extensions.HF_state_sensors.state_sensor;
                            if (extensions == null || extensions.HF_state_sensors == null || extensions.HF_state_sensors.state_sensors == null || extensions.HF_state_sensors.state_sensors.Count < sensorValue) {
                                Debug.LogWarning("Error importing camera sensor");
                            } else {
                                Debug.Log("Loading camera " + extensions.HF_state_sensors.state_sensors.Count.ToString());
                                HFStateSensors.HFStateSensor stateSensorData = extensions.HF_state_sensors.state_sensors[sensorValue];

                                StateSensor stateSensor = new StateSensor(result[i].node, stateSensorData);
                            }
                        }
                        // Lights
                        if (nodes[i].extensions.KHR_lights_punctual != null) {
                            int lightValue = nodes[i].extensions.KHR_lights_punctual.light;
                            if (extensions == null || extensions.KHR_lights_punctual == null || extensions.KHR_lights_punctual.lights == null || extensions.KHR_lights_punctual.lights.Count < lightValue) {
                                Debug.LogWarning("Error importing light");
                            } else {
                                KHRLightsPunctual.GLTFLight lightData = extensions.KHR_lights_punctual.lights[lightValue];
                                Light light = result[i].transform.gameObject.AddComponent<Light>();
                                light.gameObject.AddComponent<UniversalAdditionalLightData>();
                                result[i].transform.localRotation *= Quaternion.Euler(0, 180, 0);
                                if (!string.IsNullOrEmpty(lightData.name))
                                    light.transform.gameObject.name = lightData.name;
                                light.color = lightData.color;
                                light.intensity = lightData.intensity;
                                light.range = lightData.range;
                                light.shadows = LightShadows.Soft;
                                switch (lightData.type) {
                                    case LightType.directional:
                                        light.type = UnityEngine.LightType.Directional;
                                        break;
                                    case LightType.point:
                                        light.type = UnityEngine.LightType.Point;
                                        break;
                                    case LightType.spot:
                                        light.type = UnityEngine.LightType.Spot;
                                        break;
                                }
                            }
                        }

                        // Colliders
                        if (nodes[i].extensions.HF_colliders != null) {
                            int colliderValue = nodes[i].extensions.HF_colliders.component_id;
                            if (extensions == null || extensions.HF_colliders == null || extensions.HF_colliders.components == null || extensions.HF_colliders.components.Count < colliderValue) {
                                Debug.LogWarning("Error importing collider");
                            } else {
                                HFColliders.GLTFCollider collider = extensions.HF_colliders.components[colliderValue];
                                if (collider.mesh.HasValue) {
                                    Debug.LogWarning("Ignoring collider mesh value");
                                }
                                if (collider.type == ColliderType.box) {
                                    BoxCollider col = result[i].transform.gameObject.AddComponent<BoxCollider>();
                                    col.size = collider.boundingBox;
                                    col.center = collider.offset;
                                    col.isTrigger = collider.intangible;
                                } else if (collider.type == ColliderType.sphere) {
                                    SphereCollider col = result[i].transform.gameObject.AddComponent<SphereCollider>();
                                    col.radius = Mathf.Min(collider.boundingBox[0], collider.boundingBox[1], collider.boundingBox[2]);
                                    col.center = collider.offset;
                                    col.isTrigger = collider.intangible;
                                } else if (collider.type == ColliderType.capsule) {
                                    CapsuleCollider col = result[i].transform.gameObject.AddComponent<CapsuleCollider>();
                                    col.radius = Mathf.Min(collider.boundingBox[0], collider.boundingBox[2]);
                                    col.height = collider.boundingBox[1];
                                    col.center = collider.offset;
                                    col.isTrigger = collider.intangible;
                                } else {
                                    Debug.LogWarning(string.Format("Collider type {0} not implemented", collider.GetType()));
                                }
                            }
                        }

                        // Articulated body
                        if (nodes[i].extensions.HF_articulated_bodies != null) {
                            int componentId = nodes[i].extensions.HF_articulated_bodies.component_id;
                            if (extensions == null || extensions.HF_articulated_bodies == null || extensions.HF_articulated_bodies.components == null || extensions.HF_articulated_bodies.components.Count < componentId) {
                                Debug.LogWarning("Error importing articulated body");
                            } else {
                                HFArticulatedBodies.GLTFArticulatedBody ab = extensions.HF_articulated_bodies.components[componentId];
                                ArticulationBody articulation = result[i].transform.gameObject.AddComponent<ArticulationBody>();
                                switch (ab.joint_type) {
                                    case "fixed":
                                        articulation.jointType = ArticulationJointType.FixedJoint;
                                        break;
                                    case "prismatic":
                                        articulation.jointType = ArticulationJointType.PrismaticJoint;
                                        break;
                                    case "revolute":
                                        articulation.jointType = ArticulationJointType.RevoluteJoint;
                                        break;
                                    default:
                                        Debug.LogWarning(string.Format("Joint type {0} not implemented", ab.joint_type));
                                        break;
                                }
                                articulation.anchorPosition = ab.anchor_position;
                                articulation.anchorRotation = ab.anchor_rotation;
                                articulation.linearDamping = ab.linear_damping;
                                articulation.angularDamping = ab.angular_damping;
                                articulation.jointFriction = ab.joint_friction;
                                articulation.mass = ab.mass;
                                articulation.centerOfMass = ab.center_of_mass;
                                if (ab.inertia_tensor != null) {
                                    articulation.inertiaTensor = ab.inertia_tensor.Value;
                                }

                                ArticulationDrive xDrive = new ArticulationDrive()
                                {
                                    stiffness = ab.drive_stifness,
                                    forceLimit = ab.drive_force_limit,
                                    damping = ab.drive_damping,
                                    lowerLimit = ab.lower_limit,
                                    upperLimit = ab.upper_limit
                                };
                                articulation.xDrive = xDrive;
                            }
                        }

                        // Rigidbody
                        if (nodes[i].extensions.HF_rigid_bodies != null) {
                            int ComponentId = nodes[i].extensions.HF_rigid_bodies.component_id;
                            if (extensions == null || extensions.HF_rigid_bodies == null || extensions.HF_rigid_bodies.components == null || extensions.HF_rigid_bodies.components.Count < ComponentId) {
                                Debug.LogWarning("Error importing rigidbody");
                            } else {
                                HFRigidBodies.GLTFRigidBody rigidbody = extensions.HF_rigid_bodies.components[ComponentId];
                                Rigidbody rb = result[i].transform.gameObject.AddComponent<Rigidbody>();
                                rb.mass = rigidbody.mass;
                                rb.centerOfMass = rigidbody.center_of_mass;
                                if (rigidbody.inertia_tensor != null) {
                                    rb.inertiaTensor = rigidbody.inertia_tensor.Value;
                                }
                                rb.drag = rigidbody.linear_drag;
                                rb.angularDrag = rigidbody.angular_drag;
                                rb.useGravity = rigidbody.use_gravity;
                                rb.collisionDetectionMode = rigidbody.continuous ? CollisionDetectionMode.Continuous : CollisionDetectionMode.Discrete;
                                rb.isKinematic = rigidbody.kinematic;

                                foreach (string constraint in rigidbody.constraints) {
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

                        if (nodes[i].extensions.HF_custom != null) {
                            for (int j = 0; j < nodes[i].extensions.HF_custom.Length; j++) {
                                string json = nodes[i].extensions.HF_custom[j];
                                CustomExtensionWrapper wrapper = JsonUtility.FromJson<CustomExtensionWrapper>(json);
                                if (wrapper == null) {
                                    Debug.LogWarning($"Invalid custom extension JSON: {json}");
                                    continue;
                                }
                                if (!Simulator.GLTFExtensions.TryGetValue(wrapper.type, out Type extensionType)) {
                                    Debug.LogWarning($"Extension type {wrapper.type} not found.");
                                    continue;
                                }
                                IGLTFExtension extension = JsonConvert.DeserializeObject(wrapper.contents, extensionType) as IGLTFExtension;
                                if (Application.isPlaying)
                                    extension.Initialize(result[i].node);
                            }
                        }
                    }
                }
                if (!Application.isPlaying) {
                    for (int i = 0; i < result.Length; i++) {
                        GameObject.DestroyImmediate(result[i].node);
                    }
                }
                IsCompleted = true;
            }
        }

        public class ExportResult : GLTFNode {
            [JsonIgnore] public Transform transform;
            [JsonIgnore] public MeshRenderer renderer;
            [JsonIgnore] public MeshFilter filter;
            [JsonIgnore] public SkinnedMeshRenderer skinnedMeshRenderer;
            [JsonIgnore] public GLTFMesh meshResult;
        }

        public static List<ExportResult> Export(GLTFObject gltfObject, Transform root) {
            List<ExportResult> nodes = new List<ExportResult>();
            CreateNodeListRecursive(root, nodes);
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
            return nodes;
        }

        static void CreateNodeListRecursive(Transform transform, List<ExportResult> nodes) {
            ExportResult node = new ExportResult();
            node.transform = transform;
            node.name = transform.name;
            node.translation = transform.localPosition;
            node.rotation = transform.localRotation;
            node.scale = transform.localScale;
            node.renderer = transform.gameObject.GetComponent<MeshRenderer>();
            node.filter = transform.gameObject.GetComponent<MeshFilter>();
            node.skinnedMeshRenderer = transform.gameObject.GetComponent<SkinnedMeshRenderer>();
            nodes.Add(node);
            if (transform.childCount > 0) {
                if (transform.childCount > 0) {
                    node.children = new int[transform.childCount];
                    for (int i = 0; i < node.children.Length; i++) {
                        Transform child = transform.GetChild(i);
                        node.children[i] = nodes.Count;
                        CreateNodeListRecursive(child, nodes);
                    }
                }
            }
        }
    }

    public static class GLTFNodeExtensions {
        public static GameObject GetRoot(this GLTFNode.ImportResult[] nodes) {
            GLTFNode.ImportResult[] roots = nodes.Where(x => x.IsRoot).ToArray();
            if (roots.Length == 1) {
                return roots[0].transform.gameObject;
            } else {
                GameObject root = new GameObject("Root");
                for (int i = 0; i < roots.Length; i++)
                    roots[i].transform.parent = root.transform;
                return root;
            }
        }
    }
}