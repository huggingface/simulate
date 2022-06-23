using UnityEngine.Events;

namespace SimEnv.Agents {
    public class GetObservation : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            AgentManager.instance.GetObservation(callback);
        }
    }
}