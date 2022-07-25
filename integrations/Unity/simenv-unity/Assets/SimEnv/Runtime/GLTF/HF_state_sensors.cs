using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace SimEnv.GLTF {
    public class HFStateSensors {
        public List<HFStateSensor> state_sensors;

        public HFStateSensors() {
            state_sensors = new List<HFStateSensor>();
        }
        public class HFStateSensor {
            public string entity_name;
            public List<string> properties;
        }

    }

}