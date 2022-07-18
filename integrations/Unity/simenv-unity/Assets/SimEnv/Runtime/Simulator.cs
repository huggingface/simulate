using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEngine;

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

        /// <summary>
        /// Stores reference to loaded GLTF extensions.
        /// <para>See GLTFNode.cs for extension loading.</para>
        /// </summary>
        public static Dictionary<string, Type> GLTFExtensions;

        /// <summary>
        /// Stores reference to loaded plugins.
        /// </summary>
        public static List<IPlugin> Plugins;

        /// <summary>
        /// Framerate of the simulation.
        /// </summary>
        public static int FrameRate { get; private set; }

        /// <summary>
        /// How many frames to simulate before returning the result.
        /// </summary>
        public static int FrameSkip { get; private set; }

        static List<Environment> _activeEnvironments;
        /// <summary>
        /// Stores reference to all currently active environments.
        /// </summary>
        public static List<Environment> ActiveEnvironments {
            get {
                _activeEnvironments ??= new List<Environment>();
                return _activeEnvironments;
            }
        }

        private void Awake() {
            Physics.autoSimulation = false;
            LoadCustomAssemblies();
            LoadPlugins();
            // TODO: Option to parse simulation args directly from API
            GetCommandLineArgs(out int port, out int physicsUpdateRate, out int frameSkip);
            FrameRate = physicsUpdateRate;
            FrameSkip = frameSkip;
            Client.Initialize("localhost", port);
        }

        private void OnDestroy() {
            Unload();
            UnloadPlugins();
        }

        static void GetCommandLineArgs(out int port, out int physicsUpdateRate, out int frameSkip) {
            port = 55000;
            physicsUpdateRate = 30;
            frameSkip = 1;
            if (TryGetArg("port", out string portArg))
                int.TryParse(portArg, out port);
            if (TryGetArg("physics_update_rate", out string physicsUpdateRateArg))
                int.TryParse(physicsUpdateRateArg, out physicsUpdateRate);
            if (TryGetArg("frame_skip", out string frameSkipArg))
                int.TryParse(frameSkipArg, out frameSkip);
        }

        public static void Register(Environment environment) {
            if (ActiveEnvironments.Contains(environment)) {
                Debug.LogWarning("Environment is already registered.");
                return;
            }
            ActiveEnvironments.Add(environment);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="frames">Number of frames to step forward.</param>
        /// <param name="frameRate">Frames per second to simulate at.</param>
        public static void Step(int frameSkip = -1, int frameRate = -1) {
            if (frameSkip == -1)
                frameSkip = FrameSkip;
            if (frameRate == -1)
                frameRate = FrameRate;
            for (int i = 0; i < frameSkip; i++)
                Physics.Simulate(1f / frameRate);
        }

        /// <summary>
        /// Unloads all active environments.
        /// </summary>
        public static void Unload() {
            foreach (Environment environment in ActiveEnvironments)
                environment.Unload();
        }

        /// <summary>
        /// Finds and loads any custom DLLs in Resources/Plugins.
        /// </summary>
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

        /// <summary>
        /// Finds plugins and instantiates them.
        /// </summary>
        private static void LoadPlugins() {
            Plugins = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IPlugin).IsAssignableFrom(x))
                .Select(x => (IPlugin)Activator.CreateInstance(x))
                .ToList();
            Plugins.ForEach(plugin => plugin.OnCreated());

            GLTFExtensions = new Dictionary<string, Type>();
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IGLTFExtension).IsAssignableFrom(x))
                .ToList().ForEach(type => {
                    GLTFExtensions.Add(type.Name, type);
                });
        }

        /// <summary>
        /// Calls <c>OnReleased()</c> of all plugins.
        /// </summary>
        private static void UnloadPlugins() {
            Plugins.ForEach(plugin => plugin.OnReleased());
            Plugins.Clear();
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

        /// <summary>
        /// Helper function for getting command line arguments.
        /// </summary>
        /// <param name="name"></param>
        /// <returns></returns>
        public static bool TryGetArg(string name, out string arg) {
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