using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class GetReward : ICommand {
        public string message;
        public override void Execute(UnityAction<string> callback) {
            float reward = Simulator.GetReward();
            callback(reward.ToString());
        }
    }
}