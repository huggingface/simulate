using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class GetObservation : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            RLEnvironmentManager.instance.GetObservation(callback);
        }
    }
}