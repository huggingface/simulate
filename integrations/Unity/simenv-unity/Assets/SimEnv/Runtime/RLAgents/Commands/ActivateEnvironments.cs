using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class ActivateEnvironments : ICommand {
        public string n_agents;

        public void Execute(UnityAction<string> callback) {
            EnvironmentManager.instance.ActivateEnvironments(int.Parse(n_agents));
            callback("ack");
        }
    }
}