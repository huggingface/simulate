namespace SimEnv.RlAgents {
    public class AgentsPlugin : IPlugin {
        public void OnCreated() {
            AgentManager.instance ??= new AgentManager(); // superceded by the EnvironmentManager
            EnvironmentManager.instance ??= new EnvironmentManager();
        }

        public void OnReleased() {

        }

        public void OnEnvironmentLoaded() {
            AgentManager.instance.Initialize();
        }

        public void OnBeforeEnvironmentUnloaded() {
            AgentManager.instance.agents.Clear();
        }
    }
}