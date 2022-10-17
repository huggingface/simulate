using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using Simulate.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace Simulate {
    /// <summary>
    /// Initializes the Simulate backend. Required for all scenes.
    /// </summary>
    public class Simulator : MonoBehaviour {
        static Simulator _instance;
        public static Simulator instance {
            get {
                if (_instance == null) {
                    _instance = GameObject.FindObjectOfType<Simulator>();
                    if (_instance == null)
                        _instance = new GameObject("Simulator").AddComponent<Simulator>();
                }
                return _instance;
            }
        }

        public static event UnityAction BeforeStep;
        public static event UnityAction AfterStep;
        public static event UnityAction AfterReset;
        public static event UnityAction BeforeIntermediateFrame;
        public static event UnityAction AfterIntermediateFrame;

        public static Dictionary<string, Type> extensions;
        public static List<IPlugin> plugins;
        public static GameObject root { get; private set; }
        public static Dictionary<string, Node> nodes { get; private set; }
        public static List<RenderCamera> cameras { get; private set; }
        public static EventData currentEvent { get; private set; }

        public static Node GetNode(string name) {
            if (!TryGetNode(name, out Node node))
                Debug.LogWarning($"Node {name} not found");
            return node;
        }

        public static bool TryGetNode(string name, out Node node) {
            return nodes.TryGetValue(name, out node);
        }

        private void Awake() {
            Physics.autoSimulation = false;
            LoadCustomAssemblies();
            LoadPlugins();
            GetCommandLineArgs(out int port);
            Client.Initialize("localhost", port);
        }

        private void OnDestroy() {
            Unload();
            UnloadPlugins();
        }

        static void GetCommandLineArgs(out int port) {
            port = 55001;
            string[] args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++) {
                if (args[i] == "port")
                    int.TryParse(args[i + 1], out port);
            }
        }

        public static async Task Initialize(string b64bytes, Dictionary<string, object> kwargs) {
            if (root != null)
                throw new System.Exception("Scene is already initialized. Close before opening a new scene.");

            // Load scene from bytes
            byte[] bytes = Convert.FromBase64String(b64bytes);
            root = await Importer.LoadFromBytesAsync(bytes);

            // Gather reference to nodes and cameras
            nodes = new Dictionary<string, Node>();
            cameras = new List<RenderCamera>();
            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                nodes.Add(node.gameObject.name, node);
                if (node.camera != null) {
                    cameras.Add(node.camera);
                }
            }

            // Apply configuration, such as ambient lighting
            Config.Apply();

            // Initialize plugins
            foreach (IPlugin plugin in plugins)
                plugin.OnSceneInitialized(kwargs);
        }

        public static IEnumerator StepCoroutine(Dictionary<string, object> kwargs) {
            if (root == null)
                throw new System.Exception("Scene is not initialized. Call `show()` to initialize the scene before stepping.");

            // If config overrides found, cache and apply
            int frameSkip = Config.instance.frameSkip;
            float timeStep = Config.instance.timeStep;
            bool returnNodes = Config.instance.returnNodes;
            bool returnFrames = Config.instance.returnFrames;
            kwargs.TryParse("frame_skip", out Config.instance.frameSkip, frameSkip);
            kwargs.TryParse("time_step", out Config.instance.timeStep, timeStep);
            kwargs.TryParse("return_nodes", out Config.instance.returnNodes, returnNodes);
            kwargs.TryParse("return_frames", out Config.instance.returnFrames, returnFrames);

            if (currentEvent == null)
                currentEvent = new EventData();

            // Execute pre-step functionality
            currentEvent.inputKwargs = kwargs;
            foreach (IPlugin plugin in plugins)
                plugin.OnBeforeStep(currentEvent);
            BeforeStep?.Invoke();

            for (int i = 0; i < Config.instance.frameSkip; i++) {
                BeforeIntermediateFrame?.Invoke();
                Physics.Simulate(Config.instance.timeStep);
                AfterIntermediateFrame?.Invoke();
            }

            // Perform early post-step functionality
            currentEvent = new EventData();
            OnEarlyStepInternal(Config.instance.returnFrames);
            foreach (IPlugin plugin in plugins)
                plugin.OnStep(currentEvent);

            yield return new WaitForEndOfFrame();

            // Perform post-step functionality
            OnStepInternal(Config.instance.returnNodes, Config.instance.returnFrames);
            foreach (IPlugin plugin in plugins)
                plugin.OnAfterStep(currentEvent);

            AfterStep?.Invoke();

            // Revert config overrides
            Config.instance.frameSkip = frameSkip;
            Config.instance.timeStep = timeStep;
            Config.instance.returnFrames = returnFrames;
            Config.instance.returnNodes = returnNodes;
        }

        static void OnEarlyStepInternal(bool readCameraData) {
            if (readCameraData) {
                foreach (RenderCamera camera in cameras)
                    camera.camera.enabled = true;
            }
        }

        static void OnStepInternal(bool readNodeData, bool readCameraData) {
            if (readNodeData) {
                foreach (Node node in nodes.Values) {
                    if (Config.instance.nodeFilter == null || Config.instance.nodeFilter.Contains(node.name))
                        currentEvent.nodes.Add(node.name, node.GetData());
                }
            }
            if (readCameraData) {
                foreach (RenderCamera camera in cameras) {
                    if (camera.readable) {
                        camera.CopyRenderResultToBuffer(out uint[,,] buffer);
                        currentEvent.frames.Add(camera.node.name, buffer);
                    }
                    camera.camera.enabled = false;
                }
            }
        }

        public static void Reset() {
            foreach (Node node in nodes.Values)
                node.ResetState(Vector3.zero);
            foreach (IPlugin plugin in plugins)
                plugin.OnReset();
            AfterReset?.Invoke();
        }

        public static void Unload() {
            foreach (IPlugin plugin in Simulator.plugins)
                plugin.OnBeforeSceneUnloaded();
            if (root != null)
                GameObject.DestroyImmediate(root);
        }

        private static void LoadCustomAssemblies() {
            string modPath = Application.dataPath + "/Resources/Plugins";
            DirectoryInfo modDirectory = new DirectoryInfo(Application.dataPath + "/Resources/Plugins");
            if (!modDirectory.Exists) {
                Debug.LogWarning("Plugin directory doesn't exist at path: " + modPath);
                return;
            }
            foreach (FileInfo file in modDirectory.GetFiles()) {
                if (file.Extension == ".dll") {
                    Assembly.LoadFile(file.FullName);
                    Debug.Log("Loaded plugin assembly: " + file.Name);
                }
            }
        }

        private static void LoadPlugins() {
            plugins = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IPlugin).IsAssignableFrom(x))
                .Select(x => (IPlugin)Activator.CreateInstance(x))
                .ToList();
            plugins.ForEach(plugin => plugin.OnCreated());

            extensions = new Dictionary<string, Type>();
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IGLTFExtension).IsAssignableFrom(x))
                .ToList().ForEach(type => {
                    extensions.Add(type.Name, type);
                });
        }

        private static void UnloadPlugins() {
            plugins.ForEach(plugin => plugin.OnReleased());
            plugins.Clear();
        }

        public static void Close() {
            Unload();
            Client.Close();
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}