using System;
using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class AddToPool : ICommand {
        public string b64bytes;

        public void Execute(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            EnvironmentManager.instance.AddToPool(bytes);
            callback("ack");
        }
    }
}