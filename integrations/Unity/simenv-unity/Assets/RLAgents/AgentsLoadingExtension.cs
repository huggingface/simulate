using ISimEnv;

namespace SimEnv.Agents {
    public class AgentsLoadingExtension : ISimulatorExtension {
        public void OnCreated(ISimulator simulator) {
            AgentManager.instance ??= new AgentManager(simulator);
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