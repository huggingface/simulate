using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HF_Controllers {
        public List<HF_Controller> components;

        public HF_Controllers() {
            components = new List<HF_Controller>();
        }

        public class HF_Controller {
            [JsonProperty(Required = Required.Always)] public List<ActionMapping> mapping;
            public List<float> low;
            public List<float> high;
            public int? n;
            public List<int> shape;
            public string dtype;

        }

        public class ActionMapping {
            [JsonProperty(Required = Required.Always)] public string action;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(Vector3Converter))] public Vector3 axis;
            [JsonProperty(Required = Required.Always)] public float amplitude = 1;
            [JsonProperty(Required = Required.Always)] public float offset = 0;
            public float? upperLimit;
            public float? lowerLimit;
        }

        public class ActionSpace {
            public ActionSpace(HF_Controller actionData) {
                this.actionMap = actionData.mapping;
            }
            public List<ActionMapping> actionMap;
            public ActionMapping GetMapping(object key) {
                int index = Convert.ToInt32(key);
                return actionMap[index];
            }
        }


    }
}

