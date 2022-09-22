#nullable enable
using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace Simulate.GLTF {
    public class HFActuators {
        public List<HFActuator> objects;

        public HFActuators() {
            objects = new List<HFActuator>();
        }

        public class HFActuator {
            [JsonProperty(Required = Required.Always)] public List<ActionMapping> mapping = new List<ActionMapping>();
            public string? actuator_tag;

            // For Discrete and Multi-binary space
            public int? n;
            // public bool? multi_binary;  // Currently not implemented

            // For Multi-discrete space
            // public List<int> nvec;  // Currently not implemented

            // For Box space
            public List<float>? low;
            public List<float>? high;
            public List<int>? shape;
            public string? dtype;

            public int? seed;
        }

        public class ActionMapping {
            [JsonProperty(Required = Required.Always)]
            public string? action;

            [JsonProperty(Required = Required.Always)]
            public float amplitude = 1;

            [JsonProperty(Required = Required.Always)]
            public float offset = 0;

            [JsonConverter(typeof(Vector3Converter))]
            public Vector3? axis;

            [JsonConverter(typeof(Vector3Converter))]
            public Vector3? position;

            [JsonProperty("use_local_coordinates")]
            public bool useLocalCoordinates = true;

            [JsonProperty("is_impulse")]
            public bool isImpulse = false;

            [JsonProperty("max_velocity_threshold")]
            public float? maxVelocityThreshold;
        }

        public class Actuator {
            public Actuator(HFActuator actuatorData) {
                this.actionMap = actuatorData.mapping;
                this.actuator_tag = actuatorData.actuator_tag;
                if (actuatorData.n.HasValue) {  // || actuatorData.nvec.Count > 0) {
                    this.is_discrete = true;
                }
            }
            public List<ActionMapping> actionMap;
            public string? actuator_tag;
            public bool is_discrete = false;

            public (float, ActionMapping) GetMapping(int actionIndex, float actionValue) {
                if (is_discrete) {
                    var index = Convert.ToInt32(actionValue);
                    return (1.0f, actionMap[index]);
                } else {
                    return (actionValue, actionMap[actionIndex]);
                }
            }
        }
    }
}

