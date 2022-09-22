using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using Simulate.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace Simulate {
    public class TestEchoGLTF : ICommand {
        public string b64bytes;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            ExecuteAsync(kwargs, callback);
        }

        async void ExecuteAsync(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            // Import GLTF
            byte[] bytes = Convert.FromBase64String(b64bytes);
            GameObject root = await Importer.LoadFromBytesAsync(bytes);

            // Export GLTF
            GLTFObject gltfObject = Exporter.CreateGLTFObject(root.transform, null, true);
            JsonSerializerSettings settings = new JsonSerializerSettings() { NullValueHandling = NullValueHandling.Ignore };
            string json = JsonConvert.SerializeObject(gltfObject, settings);
            callback(json);
        }
    }
}