// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFNode.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System;
using System.Linq;

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
            public HFAction HF_actions;
            public HFRigidbody HF_rigid_bodies;
            public string[] HF_custom;
        }

        public class CustomExtensionWrapper {
            public string type;
            public string contents;
        }

        public class HFRlAgent {
            public int component_id;
        }

        public class HFRigidbody {
            public int component_id;
        }

        public class HFAction {
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
                    if (nodes[i].camera.HasValue)
                        result[i].node.cameraData = cameras[nodes[i].camera.Value];

                    // Extensions (lights, colliders, RL agents, etc)
                    if (nodes[i].extensions != null) {
                        // Lights
                        if (nodes[i].extensions.KHR_lights_punctual != null) {
                            int componentId = nodes[i].extensions.KHR_lights_punctual.light;
                            if (extensions == null || extensions.KHR_lights_punctual == null || extensions.KHR_lights_punctual.lights == null || extensions.KHR_lights_punctual.lights.Count < componentId) {
                                Debug.LogWarning("Error importing light");
                            } else {
                                result[i].node.lightData = extensions.KHR_lights_punctual.lights[componentId];
                            }
                        }

                        // Colliders
                        if (nodes[i].extensions.HF_colliders != null) {
                            int componentId = nodes[i].extensions.HF_colliders.component_id;
                            if (extensions == null || extensions.HF_colliders == null || extensions.HF_colliders.components == null || extensions.HF_colliders.components.Count < componentId) {
                                Debug.LogWarning("Error importing collider");
                            } else {
                                HFColliders.GLTFCollider collider = extensions.HF_colliders.components[componentId];
                                Mesh mesh = null;
                                if (collider.mesh.HasValue)
                                    mesh = meshTask.result[collider.mesh.Value].mesh;
                                PhysicMaterial physicMaterial = null;
                                if (collider.physicMaterial.HasValue)
                                    physicMaterial = physicMaterialTask.result[collider.physicMaterial.Value].material;
                                HFColliders.GLTFCollider.ImportResult importResult = new HFColliders.GLTFCollider.ImportResult() {
                                    collider = collider,
                                    mesh = mesh,
                                    physicMaterial = physicMaterial,
                                };
                                result[i].node.colliderData = importResult;
                            }
                        }

                        // Articulated body
                        if (nodes[i].extensions.HF_articulated_bodies != null) {
                            int componentId = nodes[i].extensions.HF_articulated_bodies.component_id;
                            if (extensions == null || extensions.HF_articulated_bodies == null || extensions.HF_articulated_bodies.components == null || extensions.HF_articulated_bodies.components.Count < componentId) {
                                Debug.LogWarning("Error importing articulated body");
                            } else {
                                result[i].node.articulatedBodyData = extensions.HF_articulated_bodies.components[componentId];
                            }
                        }

                        // Rigidbody
                        if (nodes[i].extensions.HF_rigid_bodies != null) {
                            int componentId = nodes[i].extensions.HF_rigid_bodies.component_id;
                            if (extensions == null || extensions.HF_rigid_bodies == null || extensions.HF_rigid_bodies.components == null || extensions.HF_rigid_bodies.components.Count < componentId) {
                                Debug.LogWarning("Error importing rigidbody");
                            } else {
                                result[i].node.rigidBodyData = extensions.HF_rigid_bodies.components[componentId];
                            }
                        }

                        // RL Agents
                        if (nodes[i].extensions.HF_rl_agents != null) {
                            int agentValue = nodes[i].extensions.HF_rl_agents.component_id;
                            if (extensions == null || extensions.HF_rl_agents == null || extensions.HF_rl_agents.components == null || extensions.HF_rl_agents.components.Count < agentValue) {
                                Debug.LogWarning("Error importing agent");
                            } else {
                                result[i].node.agentData = extensions.HF_rl_agents.components[agentValue];
                            }
                        }
                        // Actor Actions
                        if (nodes[i].extensions.HF_actions != null) {
                            int agentValue = nodes[i].extensions.HF_actions.component_id;
                            if (extensions == null || extensions.HF_actions == null || extensions.HF_actions.components == null || extensions.HF_actions.components.Count < agentValue) {
                                Debug.LogWarning("Error importing actor actions");
                            } else {

                                result[i].node.actionData = extensions.HF_actions.components[agentValue];
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
                                if (!Simulator.extensions.TryGetValue(wrapper.type, out Type extensionType)) {
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
            [JsonIgnore] public int? colliderMesh;
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