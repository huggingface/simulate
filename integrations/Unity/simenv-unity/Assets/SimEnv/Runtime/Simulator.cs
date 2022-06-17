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

        public static void Step(List<List<float>> actions) {
            if (ISimulator.Agents != null) {
                for (int i = 0; i < ISimulator.Agents.Count; i++) {
                    Agent agent = ISimulator.Agents[i] as Agent;
                    List<float> action = actions[i];
                    agent.SetAction(action);
                }
            } else {
                Debug.LogWarning("Attempting to step environment without an Agent");
            }
            for (int j = 0; j < FRAME_SKIP; j++) {
                if (ISimulator.Agents != null) {
                    Debug.Log("Stepping agents");
                    for (int i = 0; i < ISimulator.Agents.Count; i++) {
                        Agent agent = ISimulator.Agents[i] as Agent;
                        agent.AgentUpdate();
                    }
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
            if (ISimulator.Agents != null) {

                Instance.StartCoroutine(CoroutineGetObservation(callback));


            } else {
                Debug.LogWarning("Attempting to get observation without an Agent");
            }
        }

        public static IEnumerator CoroutineGetObservation(UnityAction<string> callback) {
            Agent exampleAgent = ISimulator.Agents[0] as Agent;
            // the coroutine has to be started from a monobehavior or something like that

            int obsSize = exampleAgent.cam.data.width * exampleAgent.cam.data.height * 3;
            uint[] pixel_values = new uint[ISimulator.Agents.Count * obsSize]; // make this a member variable somewhere


            List<Coroutine> coroutines = new List<Coroutine>();
            for (int i = 0; i < ISimulator.Agents.Count; i++) {
                Agent agent = ISimulator.Agents[i] as Agent;
                Coroutine coroutine = Instance.StartCoroutine(agent.CoroutineGetObservation(pixel_values, i * obsSize));
                coroutines.Add(coroutine);
                //yield return new WaitUntil(() => counter == ISimulator.Agents.Count);
            }

            foreach (var coroutine in coroutines) {
                yield return coroutine;
            }


            string string_array = JsonHelper.ToJson(pixel_values);
            callback(string_array);
        }
        public static IEnumerator RenderCoroutine(UnityAction<string> callback) {
            for (int i = 0; i < ISimulator.Agents.Count; i++) {
                Agent agent = ISimulator.Agents[i] as Agent;
                // Enable camera so that it renders in Unity's internal render loop
                agent.cam.enabled = true;
            }
            yield return new WaitForEndOfFrame(); // Wait for Unity to render

            CopyRenderResultToStringBuffer(callback);
            for (int i = 0; i < ISimulator.Agents.Count; i++) {
                Agent agent = ISimulator.Agents[i] as Agent;
                agent.cam.enabled = false;
            }
        }

        public static void CopyRenderResultToStringBuffer(UnityAction<string> callback) {

            Agent exampleAgent = ISimulator.Agents[0] as Agent;
            int obsSize = exampleAgent.cam.data.width * exampleAgent.cam.data.height * 3;
            uint[] pixel_values; // make this a member variable somewhere
            pixel_values = new uint[ISimulator.Agents.Count * obsSize];
            for (int j = 0; j < ISimulator.Agents.Count; j++) {
                Agent agent = ISimulator.Agents[j] as Agent;
                RenderTexture activeRenderTexture = RenderTexture.active;
                RenderTexture.active = agent.cam.cam.targetTexture;
                Texture2D image = new Texture2D(agent.cam.cam.targetTexture.width, agent.cam.cam.targetTexture.height);
                image.ReadPixels(new Rect(0, 0, image.width, image.height), 0, 0);
                image.Apply();
                Color32[] pixels = image.GetPixels32();
                RenderTexture.active = activeRenderTexture;
                Debug.Log("pixels length:" + pixels.Length.ToString());
                for (int i = 0; i < pixels.Length; i++) {
                    pixel_values[j * obsSize + i * 3] = pixels[i].r;
                    pixel_values[j * obsSize + i * 3 + 1] = pixels[i].g;
                    pixel_values[j * obsSize + i * 3 + 2] = pixels[i].b;
                    // we do not include alpha, TODO: Add option to include Depth Buffer
                }
            }

            string string_array = JsonHelper.ToJson(pixel_values);
            Debug.Log(string_array);
            if (callback != null)
                callback(string_array);
        }
        public static float GetReward() {
            float reward = 0.0f;

            // Calculate the agent's reward for the current timestep 
            if (ISimulator.Agents != null) {
                Agent agent = ISimulator.Agents[0] as Agent;
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
            if (ISimulator.Agents != null) {
                Agent agent = ISimulator.Agents[0] as Agent;
                return agent.IsDone();
            } else {
                Debug.LogWarning("Attempting to get done without an Agent");
            }
            return false;
        }

        public static void Reset() {
            // Reset the Agent & the environment # 
            // TODO add the environment reset!
            if (ISimulator.Agents != null) {
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
            Time.timeScale = TIME_SCALE;
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