using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace Simulate {
    public class Initialize : ICommand {
        public string b64bytes;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            ExecuteAsync(kwargs, callback);
        }

        async void ExecuteAsync(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            try {
                await Simulator.Initialize(b64bytes, kwargs);
            } catch (System.Exception e) {
                string error = "Failed to build scene from GLTF: " + e.ToString();
                Debug.LogError(error);
                callback(error);
                return;
            }
            callback("{}");
        }
    }
}