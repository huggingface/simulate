namespace SimEnv.Agents {
    public class AgentsLoadingExtension : ISimulatorExtension {
        public void OnCreated() {
            AgentManager.instance ??= new AgentManager();
        }

        public void OnReleased() {
            
        }

        public void OnEnvironmentLoaded() {
            AgentManager.instance.Initialize();
        }

        public void OnBeforeEnvironmentUnloaded() {
            
        }
    }
}