using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Step : ICommand {
        public float[] action;

        public override void Execute(UnityAction<string> callback) {
            Simulator.Step(action.ToList());
            callback("ack");
        }
    }
}
