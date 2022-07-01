using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace SimEnv.GLTF {
    public class KHRLightsPunctual {
        public List<GLTFLight> lights;

        public class GLTFLight {
            public string name = "";
            [JsonConverter(typeof(ColorRGBConverter))] public Color color = Color.white;
            public float intensity = 1f;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public LightType type;
            public float range;
        }
    }
}