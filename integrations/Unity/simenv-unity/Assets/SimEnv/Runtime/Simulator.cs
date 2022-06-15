using UnityEngine;

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

        SimulatorWrapper _wrapper;
        /// <summary>
        /// Wrapper to provide access through the high-level API, via ISimEnv.ISimulator.
        /// </summary>
        public SimulatorWrapper wrapper {
            get {
                _wrapper ??= new SimulatorWrapper();
                return _wrapper;
            }
        }

        private void Awake() {
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Undefined;
            LoadingManager.instance.LoadCustomAssemblies();
            LoadingManager.instance.LoadExtensions();
            Client.instance.Initialize();
        }

        private void OnDestroy() {
            LoadingManager.instance.Unload();
            LoadingManager.instance.UnloadExtensions();
        }       
    }
}