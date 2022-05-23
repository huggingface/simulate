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
        static readonly int FRAME_SKIP = 4;
        static readonly float FRAME_INTERVAL = 1f / FRAME_RATE;

        static GameObject root;

        public static void BuildSceneFromBytes(byte[] bytes) {
            if (root != null)
                GameObject.DestroyImmediate(root);
            root = Importer.LoadFromBytes(bytes);
        }

        public static void Step(List<float> action) {
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Debug.Log("Stepping agent");
                Agent agent = ISimulator.Agent as Agent;
                agent.SetAction(action);
            } else {
                Debug.LogWarning("Attempting to step environment without an Agent");
            }
            for (int i = 0; i < FRAME_SKIP; i++)
                if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                    Agent agent = ISimulator.Agent as Agent;
                    agent.AgentUpdate();
                }
            Physics.Simulate(FRAME_INTERVAL);
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
                agent.ObservationCoroutine(callback);
            } else {
                Debug.LogWarning("Attempting to get observation without an Agent");
            }

        }

        public static float GetReward() {
            // Calculate the agent's reward for the current timestep 
            // TODO: this should be caculated for each action repeat and averaged.
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                return agent.CalculateReward();
            } else {
                Debug.LogWarning("Attempting to get observation without an Agent");
            }
            return 0.0f;
        }

        public static bool GetDone() {
            // Check if the agent is in a terminal state 
            // TODO: add option for auto reset
            if (ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Agent agent = ISimulator.Agent as Agent;
                return agent.IsDone();
            } else {
                Debug.LogWarning("Attempting to get observation without an Agent");
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
                Debug.LogWarning("Attempting to get observation without an Agent");
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
            Physics.autoSimulation = false;
            client = new Client();
            modPath = Application.dataPath + "/" + modPath;
        }

        void Start() {
            LoadMods();
            LoadExtensions();
            StartClient();
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
            if(simObjectExtensions == null)
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