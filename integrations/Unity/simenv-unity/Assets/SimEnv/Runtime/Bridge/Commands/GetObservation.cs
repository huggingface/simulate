using System;
using UnityEngine.Events;
using UnityEngine;
using System.Collections.Generic;


namespace SimEnv {
    public class GetObservation : Command {
        public string message;

        public override void Execute(UnityAction<string> callback) {

            Debug.Log("Stepping ");
            RuntimeManager.Instance.GetObservation(callback);
            //callback("ack"); The callback is called when the observation is returned in a string format
        }
    }
}