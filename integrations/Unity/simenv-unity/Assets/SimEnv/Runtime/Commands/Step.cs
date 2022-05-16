using ISimEnv;
using UnityEngine.Events;

namespace SimEnv {
    public class Step : ICommand {
        public override void Execute(UnityAction<string> callback) {
            Simulator.Step();
            callback("ack");
        }
    }
}
