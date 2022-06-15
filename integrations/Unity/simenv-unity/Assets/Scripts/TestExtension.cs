using UnityEngine;
using ISimEnv;

public class TestExtension : ILoadingExtension {
    public void OnCreated(ILoading loading) {
        Debug.Log("created");
    }

    public void OnReleased() {
        Debug.Log("released");
    }

    public void OnBeforeSceneUnloaded() {
        Debug.Log("before loaded");
    }

    public void OnSceneLoaded() {
        Debug.Log("scene loaded");
    }
}
