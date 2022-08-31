using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HFControllers {
        public List<HFController> objects;

        public HFControllers() {
            objects = new List<HFController>();
        }

        public class HFController {
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
            public ActionSpace(HFController actionData) {
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

