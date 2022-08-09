using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HFRlAgents {
        public List<HFRlAgentsComponent> components;

        // A serialization of an agent components (actions possibly mapped to physics, observations devices, reward functions)
        public class HFRlAgentsComponent {
            public BoxAction box_actions;
            public DiscreteAction discrete_actions;
            public List<CameraSensor> camera_sensors;
            public List<HFRlAgentsReward> reward_functions;
        }

        public class CameraSensor {
            public string camera;
        }

        public abstract class ActionSpace {
            public abstract ActionMapping GetMapping(object key);
            public abstract List<float> Sample();
        }

        public class BoxAction : ActionSpace {
            [JsonProperty(Required = Required.Always)] public List<float> low;
            [JsonProperty(Required = Required.Always)] public List<float> high;
            [JsonProperty(Required = Required.Always)] public List<ActionMapping> action_map;

            public override ActionMapping GetMapping(object key) {
                if (!int.TryParse((string)key, out int index)) {
                    Debug.LogWarning($"Failed to parse {key} to int index");
                    return null;
                }
                return action_map[index];
            }

            public override List<float> Sample() {
                Debug.Assert(low.Count == high.Count, "Box bound dimensions don't match");
                List<float> sample = new List<float>();
                for (int i = 0; i < low.Count; i++) {
                    sample.Add(UnityEngine.Random.Range(low[i], high[i]));
                }
                return sample;
            }
        }

        public class DiscreteAction : ActionSpace {
            [JsonProperty(Required = Required.Always)] public List<ActionMapping> action_map;

            public override ActionMapping GetMapping(object key) {
                if (!int.TryParse(key.ToString(), out int index)) {
                    Debug.LogWarning($"Failed to parse {key} to int index");
                    return null;
                }
                return action_map[index];
            }

            public override List<float> Sample() {
                return new List<float> { 1f };
            }
        }

        public class ActionMapping {
            [JsonProperty(Required = Required.Always)] public string physical_action;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 axis;
            [JsonProperty(Required = Required.Always)] public float amplitude = 1;
            [JsonProperty(Required = Required.Always)] public float offset = 0;
            public float? upperLimit;
            public float? lowerLimit;
        }

        // A serialization of a reward function
        public class HFRlAgentsReward {
            [JsonProperty(Required = Required.Always)] public string entity_a;
            [JsonProperty(Required = Required.Always)] public string entity_b;
            [JsonProperty(Required = Required.Always)] public string type;
            [JsonProperty(Required = Required.Always)] public string distance_metric;
            public float scalar = 1f;
            public float threshold = 1f;
            public bool is_terminal = false;
            public bool is_collectable = false;
            public bool trigger_once = true;
            public HFRlAgentsReward reward_function_a = null;
            public HFRlAgentsReward reward_function_b = null;
        }
    }
}

