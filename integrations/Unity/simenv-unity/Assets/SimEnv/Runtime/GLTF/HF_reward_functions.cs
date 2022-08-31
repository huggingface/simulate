using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HFRewardFunctions {
        public List<HFRewardFunction> components;

        // A serialization of a reward function
        public class HFRewardFunction {
            [JsonProperty(Required = Required.Always)] public string type;
            public string entity_a;
            public string entity_b;
            public string distance_metric;
            public float scalar = 1f;
            public float threshold = 1f;
            public bool is_terminal = false;
            public bool is_collectable = false;
            public bool trigger_once = true;
        }
    }
}

