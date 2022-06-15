using UnityEngine;
using ISimEnv;

public class TestExtension : ILoadingExtension {
    ILoading loading;

    public void OnCreated(ILoading loading) {
        this.loading = loading;
    }

    public void OnReleased() {
        
    }

    public void OnBeforeSceneUnloaded() {
        
    }

    public void OnSceneLoaded() {
        if(loading.managers.simulation.TryGetNode("wall1", out INode node)) {
            Debug.Log("found node " + node.name);
        }
    }
}
