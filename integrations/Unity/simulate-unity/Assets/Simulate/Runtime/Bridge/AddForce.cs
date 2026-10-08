using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Events;

namespace Simulate {
    public class AddForce : ICommand {
        [JsonProperty(Required = Required.Always)] public string name;
        [JsonConverter(typeof(Vector3Converter)), JsonProperty(Required = Required.Always)] public Vector3 force = Vector3.zero;
        [JsonConverter(typeof(EnumConverter)), JsonProperty(PropertyName = "force_mode")] public ForceMode forceMode = ForceMode.Force;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            if (!Simulator.TryGetNode(name, out Node node) || node.rigidbody == null) {
                Debug.LogWarning($"Couldn't find node with rigidbody named {name}");
                return;
            }
            node.rigidbody.AddForce(force, forceMode);
            callback("{}");
        }
    }
}
