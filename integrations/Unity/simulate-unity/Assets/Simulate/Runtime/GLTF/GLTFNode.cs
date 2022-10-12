// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFNode.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace Simulate.GLTF {
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
        public Extras extras;

        public class Extras {
            public bool? is_actor;
        }

        public bool ShouldSerializematrix() { return matrix != Matrix4x4.identity; }
        public bool ShouldSerializetranslation() { return translation != Vector3.zero; }
        public bool ShouldSerializerotation() { return rotation != Quaternion.identity; }
        public bool ShouldSerializescale() { return scale != Vector3.one; }

        public class Extensions {
            public KHRLight KHR_lights_punctual;
            public NodeExtension HF_colliders;
            public NodeExtension HF_articulation_bodies;
            public NodeExtension HF_actuators;
            public NodeExtension HF_rigid_bodies;
            public NodeExtension HF_state_sensors;
            public NodeExtension HF_raycast_sensors;
            public NodeExtension HF_reward_functions;
            public string[] HF_custom;
        }

        public class NodeExtension {
            public string name;
            public int object_id;
        }

        public class KHRLight {
            public string name;
            public int light;
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
            HFPhysicMaterials.ImportTask physicMaterialTask;
            List<GLTFCamera> cameras;
            GLTFExtensions extensions;

            public ImportTask(List<GLTFNode> nodes, GLTFMesh.ImportTask meshTask, GLTFSkin.ImportTask skinTask,
                HFPhysicMaterials.ImportTask physicMaterialTask, List<GLTFCamera> cameras, GLTFExtensions extensions) : base(meshTask, skinTask, physicMaterialTask) {
                this.nodes = nodes;
                this.meshTask = meshTask;
                this.skinTask = skinTask;
                this.physicMaterialTask = physicMaterialTask;
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

                // Create gameObjects - give names and add node components
                result = new ImportResult[nodes.Count];
                for (int i = 0; i < result.Length; i++) {
                    result[i] = new GLTFNode.ImportResult();
                    result[i].transform = new GameObject().transform;
                    result[i].transform.gameObject.name = nodes[i].name;
                    result[i].node = result[i].transform.gameObject.AddComponent<Node>();
                    if (nodes[i].extras != null && nodes[i].extras.is_actor.HasValue && nodes[i].extras.is_actor.Value == true) {
                        result[i].node.isActor = true;
                    }
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

                // Now we add the more complex properties to the nodes (Mesh, Lights, Colliders, Cameras, Actor, etc)
                // Colliders and Mesh
                for (int i = 0; i < result.Length; i++) {
                    if (string.IsNullOrEmpty(result[i].transform.name))
                        result[i].transform.name = "node" + i;

                    if (nodes[i].mesh.HasValue && (nodes[i].extensions == null || nodes[i].extensions.HF_colliders == null)) {
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
                    }

                    // Camera
                    if (nodes[i].camera.HasValue)
                        result[i].node.cameraData = cameras[nodes[i].camera.Value];

                    // Extensions (lights, colliders, Actuators, etc)
                    if (nodes[i].extensions != null) {
                        // Colliders
                        if (nodes[i].extensions.HF_colliders != null) {
                            int componentId = nodes[i].extensions.HF_colliders.object_id;
                            if (extensions == null || extensions.HF_colliders == null || extensions.HF_colliders.objects == null || extensions.HF_colliders.objects.Count < componentId) {
                                Debug.LogWarning("Error importing collider");
                            } else {
                                HFColliders.GLTFCollider collider = extensions.HF_colliders.objects[componentId];

                                Mesh mesh = null;
                                if (nodes[i].mesh.HasValue) {
                                    GLTFMesh.ImportResult meshResult = meshTask.result[nodes[i].mesh.Value];
                                    mesh = meshResult.mesh;
                                }

                                PhysicMaterial physicMaterial = null;
                                if (collider.physic_material.HasValue)
                                    physicMaterial = physicMaterialTask.result[collider.physic_material.Value].material;

                                HFColliders.GLTFCollider.ImportResult importResult = new HFColliders.GLTFCollider.ImportResult() {
                                    collider = collider,
                                    mesh = mesh,
                                    physicMaterial = physicMaterial,
                                };

                                result[i].node.colliderData = importResult;
                            }
                        }

                        // Lights
                        if (nodes[i].extensions.KHR_lights_punctual != null) {
                            int componentId = nodes[i].extensions.KHR_lights_punctual.light;
                            if (extensions == null || extensions.KHR_lights_punctual == null || extensions.KHR_lights_punctual.lights == null || extensions.KHR_lights_punctual.lights.Count < componentId) {
                                Debug.LogWarning("Error importing light");
                            } else {
                                result[i].node.lightData = extensions.KHR_lights_punctual.lights[componentId];
                            }
                        }

                        // Articulation body
                        if (nodes[i].extensions.HF_articulation_bodies != null) {
                            int componentId = nodes[i].extensions.HF_articulation_bodies.object_id;
                            if (extensions == null || extensions.HF_articulation_bodies == null || extensions.HF_articulation_bodies.objects == null || extensions.HF_articulation_bodies.objects.Count < componentId) {
                                Debug.LogWarning("Error importing articulation body");
                            } else {
                                result[i].node.articulationBodyData = extensions.HF_articulation_bodies.objects[componentId];
                            }
                        }

                        // Rigidbody
                        if (nodes[i].extensions.HF_rigid_bodies != null) {
                            int componentId = nodes[i].extensions.HF_rigid_bodies.object_id;
                            if (extensions == null || extensions.HF_rigid_bodies == null || extensions.HF_rigid_bodies.objects == null || extensions.HF_rigid_bodies.objects.Count < componentId) {
                                Debug.LogWarning("Error importing rigidbody");
                            } else {
                                result[i].node.rigidBodyData = extensions.HF_rigid_bodies.objects[componentId];
                            }
                        }
                        // Actuators
                        if (nodes[i].extensions.HF_actuators != null) {
                            int value = nodes[i].extensions.HF_actuators.object_id;
                            if (extensions == null || extensions.HF_actuators == null || extensions.HF_actuators.objects == null || extensions.HF_actuators.objects.Count < value) {
                                Debug.LogWarning("Error importing actor actuator");
                            } else {
                                result[i].node.actuatorData = extensions.HF_actuators.objects[value];
                            }
                        }
                        // State Sensor
                        if (nodes[i].extensions.HF_state_sensors != null) {

                            int sensorValue = nodes[i].extensions.HF_state_sensors.object_id;
                            if (extensions == null || extensions.HF_state_sensors == null || extensions.HF_state_sensors.objects == null || extensions.HF_state_sensors.objects.Count < sensorValue) {
                                Debug.LogWarning("Error importing state sensor");
                            } else {
                                result[i].node.stateSensorData = extensions.HF_state_sensors.objects[sensorValue];
                            }
                        }
                        // Raycast Sensor
                        if (nodes[i].extensions.HF_raycast_sensors != null) {

                            int sensorValue = nodes[i].extensions.HF_raycast_sensors.object_id;
                            if (extensions == null || extensions.HF_raycast_sensors == null || extensions.HF_raycast_sensors.objects == null || extensions.HF_raycast_sensors.objects.Count < sensorValue) {
                                Debug.LogWarning("Error importing state sensor");
                            } else {
                                result[i].node.raycastSensorData = extensions.HF_raycast_sensors.objects[sensorValue];
                            }
                        }
                        // Reward Functions
                        if (nodes[i].extensions.HF_reward_functions != null) {

                            int rewardValue = nodes[i].extensions.HF_reward_functions.object_id;
                            if (extensions == null || extensions.HF_reward_functions == null || extensions.HF_reward_functions.objects == null || extensions.HF_reward_functions.objects.Count < rewardValue) {
                                Debug.LogWarning("Error importing reward function");
                            } else {
                                result[i].node.rewardFunctionData = extensions.HF_reward_functions.objects[rewardValue];
                            }
                        }

                        // Custom extensions
                        if (nodes[i].extensions.HF_custom != null) {
                            for (int j = 0; j < nodes[i].extensions.HF_custom.Length; j++) {
                                string json = nodes[i].extensions.HF_custom[j];
                                JObject jObject = JObject.Parse(json);
                                Dictionary<string, JToken> tokens = jObject.Properties()
                                    .ToDictionary(x => x.Name, x => x.Value);
                                if (!tokens.TryGetValue("type", out JToken type)) {
                                    string error = "Command doesn't contain type";
                                    Debug.LogWarning(error);
                                    continue;
                                }
                                Dictionary<string, object> kwargs = new Dictionary<string, object>();
                                foreach (string key in tokens.Keys) {
                                    if (key == "type")
                                        continue;
                                    object value = tokens[key].ToObject<object>();
                                    kwargs.Add(key, value);
                                }
                                if (!Simulator.extensions.TryGetValue(type.ToString(), out Type extensionType)) {
                                    Debug.LogWarning($"Extension type {type} not found.");
                                    continue;
                                }
                                jObject.Remove("type");
                                IGLTFExtension extension = JsonConvert.DeserializeObject(jObject.ToString(), extensionType) as IGLTFExtension;
                                if (Application.isPlaying)
                                    extension.Initialize(result[i].node, kwargs);
                            }
                        }
                    }
                }

                for (int i = 0; i < result.Length; i++)
                    result[i].node.Initialize();

                IsCompleted = true;
            }
        }

        public class ExportResult : GLTFNode {
            [JsonIgnore] public Transform transform;
            [JsonIgnore] public MeshRenderer renderer;
            [JsonIgnore] public MeshFilter filter;
            [JsonIgnore] public MeshCollider meshCollider;
            [JsonIgnore] public SkinnedMeshRenderer skinnedMeshRenderer;
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
            node.meshCollider = transform.gameObject.GetComponent<MeshCollider>();
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