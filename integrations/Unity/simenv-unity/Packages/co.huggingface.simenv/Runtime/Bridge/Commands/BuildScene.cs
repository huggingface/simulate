using System;
using UnityEngine.Events;

namespace SimEnv {
    public class BuildScene : Command {
        public string b64bytes;

        public override void Execute(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            RuntimeManager.BuildSceneFromBytes(bytes);
            callback("ack");
        }
    }
}