using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
using Newtonsoft.Json;

namespace Simulate.Profiling {
    public class ProfileCommand : ICommand {
        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            long receivedTime = DateTimeOffset.Now.ToUnixTimeMilliseconds();
            Dictionary<string, object> response = new Dictionary<string, object> {
                { "receivedTime", receivedTime }
            };
            callback(JsonConvert.SerializeObject(response));
        }
    }
}
