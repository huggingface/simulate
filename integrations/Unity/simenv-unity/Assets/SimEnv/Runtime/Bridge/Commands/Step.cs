using System;
using UnityEngine.Events;
using UnityEngine;
using System.Collections.Generic;


namespace SimEnv {
    public class Step : Command {
        public List<float> action;

        public override void Execute(UnityAction<string> callback) {
            Debug.Log("Stepping " + action.ToString());
            RuntimeManager.Instance.Step(action);
            callback("ack");
        }
    }
}