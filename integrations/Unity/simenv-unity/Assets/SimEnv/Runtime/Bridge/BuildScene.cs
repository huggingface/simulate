using System;
using UnityEngine.Events;
using ISimEnv;

namespace SimEnv {
    public class BuildScene : ICommand {
        public string b64bytes;

        public override void Execute(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            await Simulator.LoadEnvironmentFromBytesAsync(bytes);
            callback("ack");
        }
    }
}