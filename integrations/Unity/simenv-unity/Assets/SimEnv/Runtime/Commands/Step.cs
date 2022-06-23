using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

using System.Collections.Generic;

namespace SimEnv {


    [System.Serializable]
    public class FloatList {
        public List<float> floatList;
    }


    public class Step : ICommand {
        public float[] action;

        public override void Execute(UnityAction<string> callback) {
            // TODO: improve serialization to include nested lists / arrays
            List<List<float>> covertedActions = new List<List<float>>();

            foreach (var item in action.ToList()) {
                List<float> covertedAction = new List<float>();
                covertedAction.Add(item);
                covertedActions.Add(covertedAction);
            }

            Simulator.Step(covertedActions);
            callback("ack");
        }
    }
}
