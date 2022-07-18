using UnityEngine.Events;

namespace SimEnv {
    public class Render : ICommand {
        public string path;

        public void Execute(UnityAction<string> callback) {
            Simulator.ActiveEnvironments[0].Render(path, () => callback("ack"));
        }
    }
}