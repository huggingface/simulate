using Simulate;
using System.Collections.Generic;

public class Door : IGLTFExtension {
    public void Initialize(Node node, Dictionary<string, object> kwargs) {
        node.gameObject.AddComponent<DoorAI>();
    }
}
