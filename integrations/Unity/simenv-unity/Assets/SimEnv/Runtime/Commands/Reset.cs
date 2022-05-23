using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Reset : ICommand {
        public string message;
        public override void Execute(UnityAction<string> callback) {
            Debug.Log("Resetting ");
            Simulator.Reset();
            callback("ack");
        }
    }
}