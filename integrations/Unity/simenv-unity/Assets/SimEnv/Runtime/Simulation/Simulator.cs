using UnityEngine;
using System;
using System.Linq;
using System.Collections;
using System.IO;
using System.Reflection;
using ISimEnv;
using System.Collections.Generic;

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

        public static void Step(List<float> action) {
            if(ISimulator.Agent != null && ISimulator.Agent is Agent) {
                Debug.Log("Stepping agent");
                Agent agent = ISimulator.Agent as Agent;
                agent.SetAction(action);
            } else {
                Debug.LogWarning("Attempting to step environment without an Agent");
            }
            for(int i = 0; i < FRAME_SKIP; i++)
                Physics.Simulate(FRAME_INTERVAL);
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
            if(modDirectory.Exists) {
                foreach(FileInfo file in modDirectory.GetFiles()) {
                    if(file.Extension == ".dll") {
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
            simObjectExtensions.ToList().ForEach(x => Debug.Log(x));
            Debug.Log(simObjectExtensions.Length);
        }

        void StartClient() {
            Debug.Assert(!initialized);
            listenCoroutine = client.Listen();
            StartCoroutine(listenCoroutine);
            initialized = true;
        }

        void OnDestroy() {
            if(initialized) {
                StopCoroutine(listenCoroutine);
                client.Close();
                initialized = false;
            }
        }
        #endregion
    }
}