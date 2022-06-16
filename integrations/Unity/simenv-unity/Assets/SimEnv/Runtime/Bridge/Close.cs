using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Close : ICommand {
        public void Execute(UnityAction<string> callback) {
            Simulator.Close();
            callback("ack");
        }
    }
}
