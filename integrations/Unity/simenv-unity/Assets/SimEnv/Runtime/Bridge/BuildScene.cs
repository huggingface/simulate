using System;
using UnityEngine.Events;

namespace SimEnv {
    public class BuildScene : ICommand {
        public string b64bytes;

        public void Execute(UnityAction<string> callback) {
            ExecuteAsync(callback);
        }

        async void ExecuteAsync(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            await Environment.LoadEnvironmentFromBytesAsync(bytes);
            callback("ack");
        }
    }
}