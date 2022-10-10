using System.Collections.Generic;
using Simulate;
using UnityEngine.Events;

public class OpenDoor : ICommand {
    public string door;

    public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
        DoorsPlugin.OpenDoor(door);
        callback("{}");
    }
}
