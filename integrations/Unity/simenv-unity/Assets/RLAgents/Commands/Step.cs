using System.Collections.Generic;
using System.Linq;
using UnityEngine.Events;

namespace SimEnv.Agents {
    [System.Serializable]
    public class FloatList {
        public List<float> floatList;
    }

    public class Step : ICommand {
        public float[] action;

        public void Execute(UnityAction<string> callback) {
            // TODO: improve serialization to include nested lists / arrays
            List<List<float>> covertedActions = new List<List<float>>();

            foreach (var item in action.ToList()) {
                List<float> covertedAction = new List<float>();
                covertedAction.Add(item);
                covertedActions.Add(covertedAction);
            }

            AgentManager.instance.Step(covertedActions);
            callback("ack");
        }
    }
}
