using System.Collections.Generic;
using UnityEngine.Events;

namespace Simulate {
    public class Close : ICommand {
        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            Simulator.Close();
            callback("{}");
        }
    }
}
