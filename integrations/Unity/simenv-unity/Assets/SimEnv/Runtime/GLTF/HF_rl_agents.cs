// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFCamera.cs
using System.Collections.Generic;
using Newtonsoft.Json;

namespace SimEnv.GLTF.HFRlAgents {
    public class HFRlAgentsComponent {
        public HFRlAgentsActions actions;
        public List<string> observations;
        public List<HFRlAgentsReward> rewards;
    }
    // A serialization of a gym space with augmented mapping to physics actions if necessary
    public class HFRlAgentsActions {
        [JsonProperty(Required = Required.Always)] public string type;
        public int n;
        public List<float> low;
        public List<float> high;
        public List<int> shape;
        public string dtype;
        public List<string> physics;
        public List<float> amplitudes;
        public List<float> scaling;
        public List<float> offset;
        public List<float> clip_low = new List<float>();
        public List<float> clip_high = new List<float>();
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
    }

}

