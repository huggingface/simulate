using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace SimEnv.GLTF {
    public class HFStateSensors {
        public List<HFStateSensor> objects;

        public HFStateSensors() {
            objects = new List<HFStateSensor>();
        }
        public class HFStateSensor {
            public string reference_entity;
            public string target_entity;
            public List<string> properties;
        }

    }

}