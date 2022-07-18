using System.Collections.Generic;
using UnityEngine;
using SimEnv.GLTF;
using UnityEngine.Events;
using System.Collections;
using System.Threading.Tasks;

namespace SimEnv {
    public class Environment {
        public GameObject root;
        public Dictionary<string, Node> nodes;
        public List<RenderCamera> cameras;
        public Bounds bounds;

        public Environment(GameObject root, List<Node> nodes) {
            this.root = root;
            this.nodes = new Dictionary<string, Node>();
            cameras = new List<RenderCamera>();
            foreach (Node node in nodes) {
                this.nodes.Add(node.name, node);
                if (node.Camera != null)
                    cameras.Add(node.Camera);
            }
            bounds = GetLocalBoundsForObject(root);
            Simulator.Register(this);
        }

        public static Environment LoadEnvironmentFromBytes(byte[] bytes) {
            Environment environment = Importer.LoadFromBytes(bytes);
            foreach (IPlugin plugin in Simulator.Plugins)
                plugin.OnEnvironmentLoaded(environment);
            return environment;
        }

        public static async Task<Environment> LoadEnvironmentFromBytesAsync(byte[] bytes) {
            Environment environment = await Importer.LoadFromBytesAsync(bytes);
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

        public void Register(Node node) {
            if (nodes.TryGetValue(node.name, out Node existing))
                Debug.LogWarning($"Found existing node with name: {node.name}.");
            nodes[node.name] = node;
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
            cameras[0].Render(path, callback);
        }

        public void Render(UnityAction<List<Color32[]>> callback) {
            RenderCoroutine(callback).RunCoroutine();
        }

        private IEnumerator RenderCoroutine(UnityAction<List<Color32[]>> callback) {
            List<Color32[]> buffers = new List<Color32[]>();
            foreach (RenderCamera camera in cameras)
                camera.Render(buffer => buffers.Add(buffer));
            yield return new WaitUntil(() => buffers.Count == cameras.Count);
            callback(buffers);
        }
    }
}