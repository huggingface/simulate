using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Step : ICommand {
        public float[] action;

        public override void Execute(UnityAction<string> callback) {
            Debug.Log("Stepping " + action.ToString());
            Simulator.Step(action.ToList());
            callback("ack");
        }
    }
}
