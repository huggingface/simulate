using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class GetReward : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            float[] reward = EnvironmentManager.instance.GetReward();
            callback(JsonHelper.ToJson(reward));
        }
    }
}