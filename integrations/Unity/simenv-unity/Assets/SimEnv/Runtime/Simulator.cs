using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using SimEnv.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    /// <summary>
    /// Initializes the SimEnv backend. Required for all scenes.
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

        public static Dictionary<string, Type> extensions;
        public static List<IPlugin> plugins;
        public static GameObject root { get; private set; }
        public static Dictionary<string, Node> nodes { get; private set; }
        public static List<RenderCamera> cameras { get; private set; }
        public static EventData currentEvent { get; private set; }

        private void Awake() {
            Physics.autoSimulation = false;
            LoadCustomAssemblies();
            LoadPlugins();
            // TODO: Option to parse simulation args directly from API
            GetCommandLineArgs();
            Client.Initialize("localhost", MetaData.port);
        }

        private void OnDestroy() {
            Unload();
            UnloadPlugins();
        }

        static void GetCommandLineArgs() {
            int port = 55000;
            int frameRate = 30;
            int frameSkip = 1;
            if (TryGetArg("port", out string portArg))
                int.TryParse(portArg, out port);
            if (TryGetArg("physics_update_rate", out string physicsUpdateRateArg))
                int.TryParse(physicsUpdateRateArg, out frameRate);
            if (TryGetArg("frame_skip", out string frameSkipArg))
                int.TryParse(frameSkipArg, out frameSkip);
            MetaData.port = port;
            MetaData.frameRate = frameRate;
            MetaData.frameSkip = frameSkip;
        }

        public static async Task Initialize(string b64bytes, Dictionary<string, object> kwargs) {
            if (root != null)
                throw new System.Exception("Scene is already initialized. Close before opening a new scene.");
            byte[] bytes = Convert.FromBase64String(b64bytes);
            root = await Importer.LoadFromBytesAsync(bytes);
            nodes = new Dictionary<string, Node>();
            cameras = new List<RenderCamera>();
            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                nodes.Add(node.gameObject.name, node);
                if (node.camera != null) {
                    cameras.Add(node.camera);
                }
            }
            foreach (IPlugin plugin in plugins)
                plugin.OnSceneInitialized(kwargs);
        }

        public static IEnumerator StepCoroutine(Dictionary<string, object> kwargs) {
            if (currentEvent == null)
                yield return ReadEventData();
            currentEvent.inputKwargs = kwargs;
            foreach (IPlugin plugin in plugins)
                plugin.OnBeforeStep(currentEvent);
            BeforeStep?.Invoke();
            for (int i = 0; i < MetaData.frameSkip; i++)
                Physics.Simulate(1f / MetaData.frameRate);
            yield return ReadEventData();
            foreach (IPlugin plugin in plugins)
                plugin.OnStep(currentEvent);
            AfterStep?.Invoke();
        }

        static IEnumerator ReadEventData() {
            currentEvent = new EventData();
            if (MetaData.returnNodes) {
                foreach (Node node in nodes.Values) {
                    if (MetaData.nodeFilter == null || MetaData.nodeFilter.Contains(node.name))
                        currentEvent.nodes.Add(node.GetData());
                }
            }
            if (MetaData.returnFrames) {
                foreach (RenderCamera camera in cameras)
                    camera.camera.enabled = true;
                yield return new WaitForEndOfFrame();
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
                node.ResetState();
            foreach (IPlugin plugin in plugins)
                plugin.OnReset();
            AfterReset?.Invoke();
        }

        public static void Unload() {
            foreach (IPlugin plugin in Simulator.plugins)
                plugin.OnBeforeSceneUnloaded();
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
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        static bool TryGetArg(string name, out string arg) {
            arg = null;
            var args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++) {
                if (args[i] == name && args.Length > i + 1) {
                    arg = args[i + 1];
                    return true;
                }
            }
            return false;
        }
    }
}