namespace ISimEnv {
    public interface ILoadingExtension {
        void OnCreated(ILoading loading);
        void OnReleased();
        void OnSceneLoaded();
        void OnBeforeSceneUnloaded();
    }
}