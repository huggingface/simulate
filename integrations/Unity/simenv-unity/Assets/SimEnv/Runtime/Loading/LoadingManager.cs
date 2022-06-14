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

        GameObject root;

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
        }

        void OnAfterLoad() {
            AgentManager.instance.Initialize();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Default;
            onSceneLoaded?.Invoke();
        }

        public void Unload() {
            if(root == null) return;
            onBeforeSceneUnloaded?.Invoke();
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Unloading;
            GameObject.Destroy(root);
            SimulationManager.instance.updateMode = SimulationManager.UpdateMode.Undefined;
            onSceneUnloaded?.Invoke();
        }

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