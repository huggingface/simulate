using System.Collections.Generic;
using Simulate;
using UnityEngine;

public class DoorsPlugin : PluginBase {
    public static DoorsPlugin instance { get; private set; }
    public static Dictionary<string, DoorAI> doors { get; private set; }

    public DoorsPlugin() {
        instance = this;
        doors = new Dictionary<string, DoorAI>();
    }

    public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
        doors.Clear();
        foreach (Node node in Simulator.nodes.Values) {
            if (node.gameObject.TryGetComponent<DoorAI>(out DoorAI doorAI)) {
                doors.Add(node.name, doorAI);
            }
        }
    }

    public override void OnStep(EventData eventData) {
        foreach (DoorAI doorAI in doors.Values)
            doorAI.Step();
    }

    public static void OpenDoor(string name) {
        if (!doors.TryGetValue(name, out DoorAI doorAI)) {
            Debug.LogWarning($"Door {name} not found");
            return;
        }
        doorAI.Open();
    }
}
