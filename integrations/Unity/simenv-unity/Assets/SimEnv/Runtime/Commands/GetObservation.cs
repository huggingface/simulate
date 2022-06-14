using ISimEnv;
using UnityEngine.Events;
using UnityEngine;

namespace SimEnv {
    public class GetObservation : ICommand {
        public string message;

        public void Execute(UnityAction<string> callback) {
            Debug.Log("get observation");
            AgentManager.instance.GetObservation(buffer => {
                SerializedObservation observation = new SerializedObservation() { 
                    pixels = new uint[buffer.Length * 3] 
                };
                for (int i = 0; i < buffer.Length; i++) {
                    observation.pixels[i * 3] += buffer[i].r;
                    observation.pixels[i * 3 + 1] += buffer[i].g;
                    observation.pixels[i * 3 + 2] += buffer[i].b;
                    // we do not include alpha, TODO: Add option to include Depth Buffer
                }

                callback(JsonUtility.ToJson(observation));
            });
        }

        private class SerializedObservation {
            public uint[] pixels;
        }
    }
}