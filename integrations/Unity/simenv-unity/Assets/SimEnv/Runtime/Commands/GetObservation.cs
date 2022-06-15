using ISimEnv;
using UnityEngine.Events;
using UnityEngine;

namespace SimEnv {
    public class GetObservation : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            Debug.Log("get observation");
            AgentManager.instance.GetObservation(observation => {
                callback(JsonUtility.ToJson(observation));
            });
        }
    }
}