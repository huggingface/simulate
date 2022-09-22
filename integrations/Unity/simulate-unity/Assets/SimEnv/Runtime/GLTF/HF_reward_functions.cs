using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace Simulate.GLTF {
    public class HFRewardFunctions {
        public List<HFRewardFunction> objects;

        // A serialization of a reward function
        public class HFRewardFunction {
            [JsonProperty(Required = Required.Always)] public string type;
            public string entity_a;
            public string entity_b;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 direction;
            public string distance_metric;
            public float scalar = 1f;
            public float threshold = 1f;
            public bool is_terminal = false;
            public bool is_collectable = false;
            public bool trigger_once = true;
        }
    }
}

