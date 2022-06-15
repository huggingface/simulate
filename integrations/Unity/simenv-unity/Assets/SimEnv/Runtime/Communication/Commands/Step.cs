using ISimEnv;
using UnityEngine.Events;
using System.Linq;

namespace SimEnv {
    public class Step : ICommand {
        public float[] action;

        public void Execute(UnityAction<string> callback) {
            AgentManager.instance.SetAction(action.ToList());
            SimulationManager.instance.Step();
            callback("ack");
        }
    }
}
