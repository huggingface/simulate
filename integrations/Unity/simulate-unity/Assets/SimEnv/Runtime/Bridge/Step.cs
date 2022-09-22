using System.Collections;
using UnityEngine.Events;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace Simulate {
    public class Step : ICommand {
        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            ExecuteCoroutine(kwargs, callback).RunCoroutine();
        }

        IEnumerator ExecuteCoroutine(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            yield return Simulator.StepCoroutine(kwargs);
            string json = JsonConvert.SerializeObject(Simulator.currentEvent, new EventDataConverter());
            callback(json);
        }
    }
}