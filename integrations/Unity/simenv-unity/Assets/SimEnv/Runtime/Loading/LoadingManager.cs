using System;
using System.Collections.Generic;
using System.Linq;
using ISimEnv;
using SimEnv.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Loading Manager")]
    public class LoadingManager : Singleton<LoadingManager> {
        public event UnityAction onBeforeSceneLoaded;
        public event UnityAction onSceneLoaded;
        public event UnityAction onBeforeSceneUnloaded;
        public event UnityAction onSceneUnloaded;

        LoadingWrapper _loadingWrapper;
        public LoadingWrapper loadingWrapper {
            get {
                _loadingWrapper ??= new LoadingWrapper();
                return _loadingWrapper;
            }
        }

        List<ILoadingExtension> extensions;

        GameObject root;

        public void LoadExtensions() {
            extensions = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && typeof(ILoadingExtension).IsAssignableFrom(x))
                .Select(x => (ILoadingExtension)Activator.CreateInstance(x))
                .ToList();
            extensions.ForEach(extension => extension.OnCreated(loadingWrapper));
        }

        public void UnloadExtensions() {
            extensions.ForEach(extension => extension.OnReleased());
        }

        public void LoadSceneFromBytes(byte[] bytes) {
            if(SimulationManager.instance.updateMode > SimulationManager.UpdateMode.Default) {
                Debug.LogWarning("Attempting to load while already loading. Ignoring request.");
                return;
            }
            Unload();
            OnBeforeLoad();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Loading;
            root = Importer.LoadFromBytes(bytes);
            OnAfterLoad();
        }

        void OnBeforeLoad() {
            onBeforeSceneLoaded?.Invoke();
            SimulationManager.instance.InitializeProperties();
        }

        void OnAfterLoad() {
            AgentManager.instance.Initialize();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Default;
            for(int i = 0; i < extensions.Count; i++)
                extensions[i].OnSceneLoaded();
            onSceneLoaded?.Invoke();
        }

        public void Unload() {
            if(root == null) return;
            for(int i = 0; i < extensions.Count; i++)
                extensions[i].OnBeforeSceneUnloaded();
            onBeforeSceneUnloaded?.Invoke();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Unloading;
            GameObject.Destroy(root);
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Undefined;
            for(int i = 0; i < extensions.Count; i++)
            onSceneUnloaded?.Invoke();
        }

        public void Close() {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}