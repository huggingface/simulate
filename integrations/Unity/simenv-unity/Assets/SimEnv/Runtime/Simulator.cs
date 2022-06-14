using UnityEngine;
using System;
using System.Linq;
using System.Collections;
using System.IO;
using System.Reflection;
using ISimEnv;
using System.Collections.Generic;
using SimEnv.GLTF;
using UnityEngine.Events;
namespace SimEnv {
    /// <summary>
    /// Master Simulator component, required to use SimEnv
    /// 
    /// 1. Imports mod DLLs (custom code snippets)
    /// 2. Spawns Client to communicate with python API
    /// </summary>
    public class Simulator : MonoBehaviour {
        public static Simulator Instance { get; private set; }

        #region Simulation
        static readonly int FRAME_RATE = 30;
        static readonly float TIME_SCALE = 1.0f;
        static readonly int FRAME_SKIP = 4;
        static readonly float FRAME_INTERVAL = 1f / (FRAME_RATE);

        static GameObject root;

        public static void BuildSceneFromBytes(byte[] bytes) {
            if (root != null)
                GameObject.DestroyImmediate(root);
            root = Importer.LoadFromBytes(bytes);
        }

        public static void Step(List<float> action) {
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                agent.SetAction(action);
            } else {
                Debug.LogWarning("Attempting to step environment without an Agent");
            }
            for (int i = 0; i < FRAME_SKIP; i++) {
                if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                    Debug.Log("Stepping agent");
                    Agent agent = ISimulator.Agent as Agent;
                    agent.AgentUpdate();
                } else {
                    Debug.LogWarning("Attempting to step environment without an Agent");
                }
                Physics.Simulate(FRAME_INTERVAL);

            }

        }

        public static void Close() {
#if UNITY_EDITOR
            // Application.Quit() does not work in the editor so
            // UnityEditor.EditorApplication.isPlaying need to be set to false to end the game
            UnityEditor.EditorApplication.isPlaying = false;
#else
         Application.Quit();
#endif
        }

        public static void GetObservation(UnityAction<string> callback) {
            // Calculate the agent's observation and send to python with callback
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                agent.GetObservation(callback);
            } else {
                Debug.LogWarning("Attempting to get observation without an Agent");
            }
        }

        public static float GetReward() {
            float reward = 0.0f;

            // Calculate the agent's reward for the current timestep 
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                reward += agent.GetReward();
                agent.ZeroReward();
            } else {
                Debug.LogWarning("Attempting to get a reward without an Agent");
            }
            return reward;
        }

        public static bool GetDone() {
            // Check if the agent is in a terminal state 
            // TODO: add option for auto reset
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                return agent.IsDone();
            } else {
                Debug.LogWarning("Attempting to get done without an Agent");
            }
            return false;
        }

        public static void Reset() {
            // Reset the Agent & the environment # 
            // TODO add the environment reset!
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                agent.Reset();
            } else {
                Debug.LogWarning("Attempting to reset without an Agent");
            }
        }


        #endregion

        #region Initialization
        [Header("Mod Path")]
        public string modPath = "Resources/Mods";

        Type[] simObjectExtensions;
        public static Type[] SimObjectExtensions => Instance.simObjectExtensions;

        Client client;
        IEnumerator listenCoroutine;
        bool initialized;

        void Awake() {
            Instance = this;
            Time.timeScale = TIME_SCALE;
            Physics.autoSimulation = false;

            var portArg = GetArg("port");
            int clientPort = 55000;

            if (portArg is not null) clientPort = int.Parse(portArg);

            Debug.Log("starting Client on Port " + clientPort.ToString());
            client = new Client(port: clientPort);
            modPath = Application.dataPath + "/" + modPath;
        }

        void Start() {
            Debug.Log("Starting Simulator");

            LoadMods();
            LoadExtensions();
            StartClient();
        }
        // Helper function for getting the command line arguments
        private static string GetArg(string name) {
            var args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++) {
                if (args[i] == name && args.Length > i + 1) {
                    return args[i + 1];
                }
            }
            return null;
        }
        void LoadMods() {
            DirectoryInfo modDirectory = new DirectoryInfo(modPath);
            if (modDirectory.Exists) {
                foreach (FileInfo file in modDirectory.GetFiles()) {
                    if (file.Extension == ".dll") {
                        Assembly.LoadFile(file.FullName);
                        Debug.Log("Loaded mod assembly: " + file.Name);
                    }
                }
            } else {
                Debug.LogWarning("Mod directory doesn't exist at path: " + modPath);
            }
        }

        void LoadExtensions() {
            simObjectExtensions = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => x.GetInterfaces().Contains(typeof(ISimObjectExtension)))
                .ToArray();
            if (simObjectExtensions == null)
                simObjectExtensions = new Type[0];
            simObjectExtensions.ToList().ForEach(x => Debug.Log(x));
            Debug.Log(string.Format("Loaded {0} extensions", simObjectExtensions.Length));
        }

        void StartClient() {
            Debug.Assert(!initialized);
            listenCoroutine = client.Listen();
            StartCoroutine(listenCoroutine);
            initialized = true;
        }

        void OnDestroy() {
            if (initialized) {
                StopCoroutine(listenCoroutine);
                client.Close();
                initialized = false;
            }
        }
        #endregion
    }
}