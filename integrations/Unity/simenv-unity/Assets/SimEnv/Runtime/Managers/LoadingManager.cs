using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using ISimEnv;
using SimEnv.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    /// <summary>
    /// Manages environment loading and unloading.
    /// <para>See <c>LoadingWrapper</c> for the High-Level API.</para>
    /// </summary>
    [CreateAssetMenu(menuName = "SimEnv/Loading Manager")]
    public class LoadingManager : Singleton<LoadingManager> {
        public event UnityAction onBeforeEnvironmentLoaded;
        public event UnityAction onEnvironmentLoaded;
        public event UnityAction onBeforeEnvironmentUnloaded;
        public event UnityAction onEnvironmentUnloaded;

        public Dictionary<string, Type> gltfExtensions;
        List<ISimulatorExtension> loadingExtensions;

        GameObject root;

        /// <summary>
        /// Finds and loads any custom DLLs in Resources/Mods.
        /// </summary>
        public void LoadCustomAssemblies() {
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
        public void LoadExtensions() {
            loadingExtensions = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(ISimulatorExtension).IsAssignableFrom(x))
                .Select(x => (ISimulatorExtension)Activator.CreateInstance(x))
                .ToList();
            loadingExtensions.ForEach(extension => extension.OnCreated(Simulator.instance.wrapper));

            gltfExtensions = new Dictionary<string, Type>();
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(IGLTFNodeExtension).IsAssignableFrom(x))
                .ToList().ForEach(type => {
                    gltfExtensions.Add(type.Name, type);
                });
        }

        /// <summary>
        /// Calls <c>OnReleased()</c> of all extensions.
        /// </summary>
        public void UnloadExtensions() {
            loadingExtensions.ForEach(extension => extension.OnReleased());
            loadingExtensions.Clear();
        }

        /// <summary>
        /// Synchronously loads a scene from bytes.
        /// </summary>
        /// <param name="bytes">GLTF scene as bytes.</param>
        public void LoadEnvironmentFromBytes(byte[] bytes) {
            if(SimulationManager.instance.updateMode > SimulationManager.UpdateMode.Default) {
                Debug.LogWarning("Attempting to load while already loading. Ignoring request.");
                return;
            }
            Unload();
            OnBeforeLoad();
            root = Importer.LoadFromBytes(bytes);
            OnAfterLoad();
        }

        /// <summary>
        /// Asynchronously loads an environment from bytes.
        /// </summary>
        /// <param name="bytes">GLTF scene as bytes.</param>
        /// <returns></returns>
        public async Task LoadEnvironmentFromBytesAsync(byte[] bytes) {
            if(SimulationManager.instance.updateMode > SimulationManager.UpdateMode.Default) {
                Debug.LogWarning("Attempting to load while already loading. Ignoring request.");
                return;
            }
            Unload();
            OnBeforeLoad();
            root = await Importer.LoadFromBytesAsync(bytes);
            OnAfterLoad();
        }

        private void OnBeforeLoad() {
            onBeforeEnvironmentLoaded?.Invoke();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Loading;
        }

        private void OnAfterLoad() {
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Default;
            Physics.autoSimulation = false;
            for(int i = 0; i < loadingExtensions.Count; i++)
                loadingExtensions[i].OnEnvironmentLoaded();
            onEnvironmentLoaded?.Invoke();
        }

        /// <summary>
        /// Unloads the current loaded environment.
        /// </summary>
        public void Unload() {
            if(root == null) return;
            for(int i = 0; i < loadingExtensions.Count; i++)
                loadingExtensions[i].OnBeforeEnvironmentUnloaded();
            onBeforeEnvironmentUnloaded?.Invoke();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Unloading;
            GameObject.DestroyImmediate(root);
            SimulationManager.instance.nodes.Clear();
            RenderManager.instance.cameras.Clear();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Undefined;
            for(int i = 0; i < loadingExtensions.Count; i++)
                onEnvironmentUnloaded?.Invoke();
        }

        /// <summary>
        /// Kills the executable.
        /// </summary>
        public void Close() {
            Unload();
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}