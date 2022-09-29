using System.Collections.Generic;
using UnityEngine.Events;

namespace Simulate.RlAgents {
    public class Reset : ICommand {
        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            Simulator.Reset();
            callback("{}");
        }
    }
}