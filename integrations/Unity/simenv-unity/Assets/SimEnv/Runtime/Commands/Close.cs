using ISimEnv;
using UnityEngine;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Close : ICommand {
        public string close;

        public override void Execute(UnityAction<string> callback) {
            Debug.Log("Closing Unity backend ");
            Simulator.Close();
            callback("ack");
        }
    }
}
