using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class Reset : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            RLEnvironmentManager.instance.ResetAgents();
            callback("ack");
        }
    }
}