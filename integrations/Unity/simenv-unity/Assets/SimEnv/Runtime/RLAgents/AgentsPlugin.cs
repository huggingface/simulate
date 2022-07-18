namespace SimEnv.RlAgents {
    public class AgentsPlugin : IPlugin {
        public void OnCreated() {
            RLEnvironmentManager.instance ??= new RLEnvironmentManager();
        }

        public void OnReleased() {

        }

        public void OnEnvironmentLoaded(Environment environment) {
            
        }

        public void OnBeforeEnvironmentUnloaded(Environment environment) {
            
        }
    }
}