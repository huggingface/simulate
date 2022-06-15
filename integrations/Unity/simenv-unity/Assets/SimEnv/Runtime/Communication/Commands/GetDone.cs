using ISimEnv;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class GetDone : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            bool done = AgentManager.instance.GetDone();
            callback(done.ToString());
        }
    }
}