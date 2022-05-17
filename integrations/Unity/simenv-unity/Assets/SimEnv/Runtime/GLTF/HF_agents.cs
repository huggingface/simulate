using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;


namespace SimEnv.GLTF {
    public class HF_agents {
        public List<GLTFAgent> agents;

        public class GLTFAgent {
            //public string name = "";
            [JsonConverter(typeof(ColorRGBConverter))] public Color color = Color.white;
            public float height = 1f;
            public float move_speed = 1f;
            public float turn_speed = 1f;
            public string action_name = "";
            public string action_dist = "";
            public List<string> available_actions = new List<string>();
        }
    }
}