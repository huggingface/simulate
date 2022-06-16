using System;
using UnityEngine.Events;
using ISimEnv;

namespace SimEnv {
    public class BuildScene : ICommand {
        public string b64bytes;

        public void Execute(UnityAction<string> callback) {
            ExecuteAsync(callback);
        }

        async void ExecuteAsync(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            await Simulator.LoadEnvironmentFromBytesAsync(bytes);
            callback("ack");
        }
    }
}