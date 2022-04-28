using System;
using UnityEngine.Events;

public class BuildScene : Command
{
    public string b64bytes;

    public override void Execute(UnityAction<string> callback) {
        byte[] bytes = Convert.FromBase64String(b64bytes);
        SimEnv.BuildSceneFromBytes(bytes);
        callback("ack");
    }
}
