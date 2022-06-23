using UnityEngine.Events;

namespace SimEnv {
    public class Close : ICommand {
        public void Execute(UnityAction<string> callback) {
            Simulator.Close();
            callback("ack");
        }
    }
}
