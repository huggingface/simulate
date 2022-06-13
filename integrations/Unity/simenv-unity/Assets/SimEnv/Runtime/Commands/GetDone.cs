using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class GetDone : ICommand {
        public string message;
        public override void Execute(UnityAction<string> callback) {
            bool done = Simulator.GetDone();
            callback(done.ToString());
        }
    }
}