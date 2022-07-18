using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class ActivateEnvironments : ICommand {
        public string n_maps;

        public void Execute(UnityAction<string> callback) {
            RLEnvironmentManager.instance.ActivateEnvironments(int.Parse(n_maps));
            callback("ack");
        }
    }
}