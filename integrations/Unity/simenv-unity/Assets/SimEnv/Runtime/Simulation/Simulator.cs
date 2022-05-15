using UnityEngine;
using SimEnv.GLTF;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using System.Threading.Tasks;
using System;
using System.Reflection;

namespace SimEnv {
    /// <summary>
    /// Master Simulator component, required to use SimEnv
    /// 
    /// 1. Imports mod DLLs (custom code snippets)
    /// 2. Spawns Client to communicate with python API
    /// </summary>
    public class Simulator : MonoBehaviour {
        public static Simulator Instance { get; private set; }

        [Header("Mod Path")]
        public string modPath = "Resources/Mods";

        Client client;
        IEnumerator listenCoroutine;
        bool initialized;

        void Awake() {
            Instance = this;            
            client = new Client();
            modPath = Application.dataPath + "/" + modPath;
        }

        void Start() {
            LoadMods();
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
    }
}