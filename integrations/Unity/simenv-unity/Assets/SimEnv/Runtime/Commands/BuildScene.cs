using System;
using UnityEngine.Events;
using SimEnv.GLTF;
using ISimEnv;

namespace SimEnv {
    public class BuildScene : ICommand {
        public string b64bytes;

        public override void Execute(UnityAction<string> callback) {
            byte[] bytes = Convert.FromBase64String(b64bytes);
            Importer.LoadFromBytes(bytes);
            callback("ack");
        }
    }
}