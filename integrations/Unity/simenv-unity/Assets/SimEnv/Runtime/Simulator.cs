using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
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
                if(_instance == null) {
                    _instance = GameObject.FindObjectOfType<Simulator>();
                    if(_instance == null)
                        _instance = new GameObject("Simulator").AddComponent<Simulator>();
                }
                return _instance;
            }
        }

        public static event UnityAction BeforeEnvironmentLoaded;
        public static event UnityAction EnvironmentLoaded;
        public static event UnityAction BeforeEnvironmentUnloaded;
        public static event UnityAction EnvironmentUnloaded;

        /// <summary>
        /// Stores reference to loaded GLTF extensions.
        /// <para>See GLTFNode.cs for extension loading.</para>
        /// </summary>
        public static Dictionary<string, Type> GLTFExtensions;

        /// <summary>
        /// Stores reference to loaded simulator extensions.
        /// </summary>
        public static List<ISimulatorExtension> SimulatorExtensions;

        /// <summary>
        /// Stores reference to all tracked cameras in the current environment.
        /// </summary>
        public static Dictionary<Camera, RenderCamera> Cameras;

        /// <summary>
        /// Stores reference to all tracked nodes in the current environment.
        /// </summary>
        public static Dictionary<string, Node> Nodes;

        /// <summary>
        /// The root gameobject of the currently loaded scene.
        /// </summary>
        public static GameObject Root;

        /// <summary>
        /// Whether the current environment is undefined, active, loading, or unloading.
        /// </summary>
        public static State CurrentState;

        private void Awake() {
            Cameras = new Dictionary<Camera, RenderCamera>();
            Nodes = new Dictionary<string, Node>();
            CurrentState = State.Undefined;
            LoadCustomAssemblies();
            LoadExtensions();
            Client.instance.Initialize();
        }

        private void OnDestroy() {
            Unload();
            UnloadExtensions();
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="frames">Number of frames to step forward.</param>
        /// <param name="frameRate">Frames per second to simulate at.</param>
        public static void Step(int frames = 1, float frameRate = 30) {
            for(int i = 0; i < frames; i++) {
                Physics.Simulate(1 / frameRate);
            }
        }

        public static void Register(RenderCamera camera) {
            if(Cameras.TryGetValue(camera.camera, out RenderCamera existing))
                Debug.LogWarning($"Found existing camera on node with name: {camera.node.name}.");
            Cameras[camera.camera] = camera;
        }

        public static void Register(Node node) {
            if(Nodes.TryGetValue(node.name, out Node existing))
                Debug.LogWarning($"Found existing node with name: {node.name}.");
            Nodes[node.name] = node;
        }

        /// <summary>
        /// Render all cameras and returns their color buffers.
        /// </summary>
        /// <param name="callback">List of camera color buffers.</param>
        public static void Render(UnityAction<List<Color32[]>> callback) {
            RenderCoroutine(callback).RunCoroutine();
        }

        private static IEnumerator RenderCoroutine(UnityAction<List<Color32[]>> callback) {
            List<Color32[]> buffers = new List<Color32[]>();
            foreach(RenderCamera camera in Cameras.Values)
                camera.Render(buffer => buffers.Add(buffer));
            yield return new WaitUntil(() => buffers.Count == Cameras.Count);
            callback(buffers);
        }

        /// <summary>
        /// Synchronously loads a scene from bytes.
        /// </summary>
        /// <param name="bytes">GLTF scene as bytes.</param>
        public static void LoadEnvironmentFromBytes(byte[] bytes) {
            if(CurrentState > State.Default) {
                Debug.LogWarning("Attempting to load while already loading. Ignoring request.");
                return;
            }
            Unload();
            OnBeforeLoad();
            Root = GLTF.Importer.LoadFromBytes(bytes);
            OnAfterLoad();
        }

        /// <summary>
        /// Asynchronously loads an environment from bytes.
        /// </summary>
        /// <param name="bytes">GLTF scene as bytes.</param>
        /// <returns></returns>
        public static async Task LoadEnvironmentFromBytesAsync(byte[] bytes) {
            if(CurrentState > State.Default) {
                Debug.LogWarning("Attempting to load while already loading. Ignoring request.");
                return;
            }
            Unload();
            OnBeforeLoad();
            Root = await GLTF.Importer.LoadFromBytesAsync(bytes);
            OnAfterLoad();
        }

        private static void OnBeforeLoad() {
            BeforeEnvironmentLoaded?.Invoke();
            CurrentState = State.Loading;
        }

        private static void OnAfterLoad() {
            CurrentState = State.Default;
            Physics.autoSimulation = false;
            for(int i = 0; i < SimulatorExtensions.Count; i++)
                SimulatorExtensions[i].OnEnvironmentLoaded();
            EnvironmentLoaded?.Invoke();
        }

        /// <summary>
        /// Unloads the current loaded environment.
        /// </summary>
        public static void Unload() {
            if(Root == null) return;
            for(int i = 0; i < SimulatorExtensions.Count; i++)
                SimulatorExtensions[i].OnBeforeEnvironmentUnloaded();
            BeforeEnvironmentUnloaded?.Invoke();
            CurrentState = State.Unloading;
            GameObject.DestroyImmediate(Root);
            Nodes.Clear();
            Cameras.Clear();
            CurrentState = State.Undefined;
            for(int i = 0; i < SimulatorExtensions.Count; i++)
                EnvironmentUnloaded?.Invoke();
        }

        /// <summary>
        /// Finds and loads any custom DLLs in Resources/Mods.
        /// </summary>
        private static void LoadCustomAssemblies() {
            string modPath = Application.dataPath + "/Resources/Mods";
            DirectoryInfo modDirectory = new DirectoryInfo(Application.dataPath + "/Resources/Mods");
            if(!modDirectory.Exists) {
                Debug.LogWarning("Mod directory doesn't exist at path: " + modPath);
                return;
            }
            foreach(FileInfo file in modDirectory.GetFiles()) {
                if(file.Extension == ".dll") {
                    Assembly.LoadFile(file.FullName);
                    Debug.Log("Loaded mod assembly: " + file.Name);
                }
            }
        }

        /// <summary>
        /// Finds custom extensions and instantiates them.
        /// </summary>
        private static void LoadExtensions() {
            SimulatorExtensions = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(ISimulatorExtension).IsAssignableFrom(x))
                .Select(x => (ISimulatorExtension)Activator.CreateInstance(x))
                .ToList();
            SimulatorExtensions.ForEach(extension => extension.OnCreated());

            GLTFExtensions = new Dictionary<string, Type>();
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IGLTFExtension).IsAssignableFrom(x))
                .ToList().ForEach(type => {
                    GLTFExtensions.Add(type.Name, type);
                });
        }

        /// <summary>
        /// Calls <c>OnReleased()</c> of all extensions.
        /// </summary>
        private static void UnloadExtensions() {
            SimulatorExtensions.ForEach(extension => extension.OnReleased());
            SimulatorExtensions.Clear();
        }

        /// <summary>
        /// Kills the executable.
        /// </summary>
        public static void Close() {
            Unload();
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        public enum State {
            Undefined,
            Default,
            Loading,
            Unloading
        }
    }
}