using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class SetNodeActive : ICommand {
        public string node;
        public bool active;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            if (!Simulator.nodes.TryGetValue(node, out Node value)) {
                Debug.LogWarning($"Node {node} not found");
                return;
            }
            value.gameObject.SetActive(active);
            callback("ack");
        }
    }
}