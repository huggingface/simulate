using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
using Newtonsoft.Json;

namespace Simulate.Profiling {
    public class ProfileCommand : ICommand {
        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            long receivedTime = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            Debug.Log($"Unity received time: {receivedTime}");

            long responseTime = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            Debug.Log($"Unity response time: {responseTime}");

            Dictionary<string, object> response = new Dictionary<string, object> {
                { "receivedTime", receivedTime },
                { "responseTime", responseTime }
            };
            callback(JsonConvert.SerializeObject(response));
        }
    }
}
