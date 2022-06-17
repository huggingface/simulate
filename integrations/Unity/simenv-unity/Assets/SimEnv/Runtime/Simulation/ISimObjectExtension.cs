namespace ISimEnv {
    public interface ISimObjectExtension {
        void OnCreated(ISimObject simObject);
        void OnInteract(params object[] args);
        void OnReleased();
    }
}