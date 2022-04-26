using UnityEngine;
using UnityEngine.Events;

public class ConstructScene : Command
{
    public string json;

    public override void Execute(UnityAction<string> callback) {
        SimEnv.ConstructScene(json);
        callback("ack");
    }
}
