using ISimEnv;
using UnityEngine.Events;

namespace SimEnv {
    public class Reset : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            AgentManager.instance.ResetAgents();
            callback("ack");
        }
    }
}