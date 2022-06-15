using ISimEnv;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class GetReward : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            float reward = AgentManager.instance.GetReward();
            callback(reward.ToString());
        }
    }
}