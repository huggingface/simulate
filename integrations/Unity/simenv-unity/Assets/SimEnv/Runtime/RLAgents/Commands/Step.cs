using System.Collections.Generic;
using System.Linq;
using UnityEngine.Events;

namespace SimEnv.RlAgents {
    [System.Serializable]
    public class FloatList {
        public List<float> floatList;
    }

    public class Step : ICommand {
        public float[] action;

        public void Execute(UnityAction<string> callback) {
            if(action == null) {
                Simulator.Step();
                callback("ack");
                return;
            }

            // TODO: improve serialization to include nested lists / arrays
            List<List<float>> converted = new List<List<float>>();

            foreach (var item in action.ToList()) {
                List<float> convertedAction = new List<float>();
                convertedAction.Add(item);
                converted.Add(convertedAction);
            }

            RLEnvironmentManager.instance.Step(converted);
            callback("ack");
        }
    }
}
