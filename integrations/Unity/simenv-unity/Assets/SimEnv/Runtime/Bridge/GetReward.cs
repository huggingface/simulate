using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class GetReward : ICommand {
        public string message;
        public override void Execute(UnityAction<string> callback) {
            Debug.Log("Getting reward ");
            float reward = Simulator.GetReward();
            callback(reward.ToString());
        }
    }
}