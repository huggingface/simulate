using UnityEngine;
using System.IO;
using System.Reflection;

namespace SimEnv {
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

        public string modPath = "Resources/Mods";

        void Awake() {
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Undefined;
            Physics.autoSimulation = false;
            modPath = Application.dataPath + "/" + modPath;
        }

        void Start() {
            LoadMods();
            CommandManager.instance.Initialize();
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
    }
}