using ISimEnv;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class Reset : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            Debug.Log("reset");
            AgentManager.instance.ResetAgents();
            callback("ack");
        }
    }
}