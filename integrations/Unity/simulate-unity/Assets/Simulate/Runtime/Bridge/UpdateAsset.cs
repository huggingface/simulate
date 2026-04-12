using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Newtonsoft.Json;

namespace Simulate {
    public class UpdateAsset : ICommand {
        [JsonProperty(Required = Required.Always)] public string name;
        [JsonConverter(typeof(Matrix4x4Converter))] public Matrix4x4 matrix = Matrix4x4.identity;
        [JsonConverter(typeof(Vector3Converter))] public Vector3 position = Vector3.zero;
        [JsonConverter(typeof(QuaternionConverter))] public Quaternion rotation = Quaternion.identity;
        [JsonConverter(typeof(Vector3Converter))] public Vector3 scale = Vector3.one;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            if (!Simulator.TryGetNode(name, out Node node)) {
                Debug.LogWarning($"Node {name} not found");
                return;
            }
            if (matrix != Matrix4x4.identity)
                matrix.UnpackMatrix(ref position, ref rotation, ref scale);
            node.transform.localPosition = position;
            node.transform.localRotation = rotation;
            node.transform.localScale = scale;
            callback("{}");
        }
    }
}