using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class GetDone : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            bool[] done = EnvironmentManager.instance.GetDone();
            callback(JsonHelper.ToJson(done));
        }
    }
}