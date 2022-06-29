// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFCamera.cs
using Newtonsoft.Json;

namespace SimEnv.GLTF {
    public class HFRlAgentsRlComponent {
        public HFRlAgentsActionSpace? action_space;
        public List<HFRlAgentsActionMapping> action_mappings;
        public List<string> observation_devices;
        public List<HFRlAgentsRewardFunction> reward_functions;

        // A serialization of a gym space
        public class HFRlAgentsActionSpace {
            [JsonProperty(Required = Required.Always)] public string type;
            public int n;
            public List<float> low;
            public List<float> high;
            public List<int> shape;
            public string dtype;
        }

        // A serialization of a mapping between gym space actions and physics
        public class HFRlAgentsActionMapping {
            [JsonProperty(Required = Required.Always)] public string physics;
            public float clip_low;
            public float clip_high;
            public float scaling = 1f;
            public float offset = 0f;
            public float value = 1f;
        }

        // A serialization of a reward function
        public class HFRlAgentsRewardFunction {
            [JsonProperty(Required = Required.Always)] public string entity_a;
            [JsonProperty(Required = Required.Always)] public string entity_b;
            [JsonProperty(Required = Required.Always)] public string type;
            [JsonProperty(Required = Required.Always)] public string distance_metric;
            public float scalar = 1f;
            public float threshold = 1f;
            public bool is_terminal = false;
        }

    }
}