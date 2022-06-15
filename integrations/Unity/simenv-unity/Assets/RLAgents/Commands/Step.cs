using System.Linq;
using ISimEnv;
using UnityEngine.Events;

namespace SimEnv.Agents {
    public class Step : ICommand {
        public float[] action;

        public void Execute(UnityAction<string> callback) {
            AgentManager.instance.SetAction(action.ToList());
            AgentManager.instance.Step();
            callback("ack");
        }
    }
}
