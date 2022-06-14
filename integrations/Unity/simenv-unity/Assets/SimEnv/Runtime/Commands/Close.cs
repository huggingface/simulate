using ISimEnv;
using UnityEngine.Events;

namespace SimEnv {
    public class Close : ICommand {
        public void Execute(UnityAction<string> callback) {
            LoadingManager.instance.Close();
            callback("ack");
        }
    }
}
