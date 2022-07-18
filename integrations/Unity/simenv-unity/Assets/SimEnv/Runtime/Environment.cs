using System.Collections.Generic;
using UnityEngine;
using SimEnv.GLTF;
using UnityEngine.Events;
using System.Linq;
using System.Collections;
using System.Threading.Tasks;

namespace SimEnv {
    public class Environment {
        public GameObject root;
        public Dictionary<string, Node> nodes;
        public Dictionary<Camera, RenderCamera> cameras;
        public Dictionary<Node, HFRlAgents.HFRlAgentsComponent> agents;
        public Bounds bounds;

        public Environment(GameObject root) {
            this.root = root;
            nodes = new Dictionary<string, Node>();
            cameras = new Dictionary<Camera, RenderCamera>();
            agents = new Dictionary<Node, HFRlAgents.HFRlAgentsComponent>();
            bounds = GetLocalBoundsForObject(root);
            Simulator.Register(this);
        }

        public static Environment LoadEnvironmentFromBytes(byte[] bytes) {
            GameObject root = Importer.LoadFromBytes(bytes);
            Environment environment = new Environment(root);
            foreach (IPlugin plugin in Simulator.Plugins)
                plugin.OnEnvironmentLoaded(environment);
            return environment;
        }

        public static async Task<Environment> LoadEnvironmentFromBytesAsync(byte[] bytes) {
            GameObject root = await Importer.LoadFromBytesAsync(bytes);
            Environment environment = new Environment(root);
            foreach (IPlugin plugin in Simulator.Plugins)
                plugin.OnEnvironmentLoaded(environment);
            return environment;
        }

        static Bounds GetLocalBoundsForObject(GameObject go) {
            var referenceTransform = go.transform;
            var b = new Bounds(Vector3.zero, Vector3.zero);
            RecurseEncapsulate(referenceTransform, ref b);
            return b;

            void RecurseEncapsulate(Transform child, ref Bounds bounds) {
                var mesh = child.GetComponent<MeshFilter>();
                if (mesh) {
                    var lsBounds = mesh.sharedMesh.bounds;
                    var wsMin = child.TransformPoint(lsBounds.center - lsBounds.extents);
                    var wsMax = child.TransformPoint(lsBounds.center + lsBounds.extents);
                    bounds.Encapsulate(referenceTransform.InverseTransformPoint(wsMin));
                    bounds.Encapsulate(referenceTransform.InverseTransformPoint(wsMax));
                }
                foreach (Transform grandChild in child.transform) {
                    RecurseEncapsulate(grandChild, ref bounds);
                }
            }
        }

        public void Unload() {
            foreach (IPlugin plugin in Simulator.Plugins)
                plugin.OnBeforeEnvironmentUnloaded(this);
            GameObject.DestroyImmediate(root);
        }

        public void Register(RenderCamera camera) {
            if (cameras.TryGetValue(camera.camera, out RenderCamera existing))
                Debug.LogWarning($"Found existing camera on node with name: {camera.node.name}.");
            cameras[camera.camera] = camera;
        }

        public void Register(Node node) {
            if (nodes.TryGetValue(node.name, out Node existing))
                Debug.LogWarning($"Found existing node with name: {node.name}.");
            nodes[node.name] = node;
        }

        public void Register(Node node, HFRlAgents.HFRlAgentsComponent agentData) {
            if (agents.ContainsKey(node)) {
                Debug.LogWarning($"Found existing agent data with name: {node.name}.");
                return;
            }
            agents.Add(node, agentData);
        }

        public void Render(string path, UnityAction callback) {
            if (cameras.Count == 0) {
                Debug.LogWarning("No cameras found.");
                callback();
                return;
            } else if (cameras.Count > 1) {
                // TODO: Add support for rendering with multiple cameras
                Debug.LogWarning("Rendering with multiple cameras not implemented. Rendering with first.");
            }
            cameras.ElementAt(0).Value.Render(path, callback);
        }

        public void Render(UnityAction<List<Color32[]>> callback) {
            RenderCoroutine(callback).RunCoroutine();
        }

        private IEnumerator RenderCoroutine(UnityAction<List<Color32[]>> callback) {
            List<Color32[]> buffers = new List<Color32[]>();
            foreach (RenderCamera camera in cameras.Values)
                camera.Render(buffer => buffers.Add(buffer));
            yield return new WaitUntil(() => buffers.Count == cameras.Count);
            callback(buffers);
        }
    }
}