using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

public class KHR_lights_punctual
{
    public List<GLTFLight> lights;

    public class GLTFLight
    {
        public string name = "";
        [JsonConverter(typeof(ColorRGBConverter))] public Color color = Color.white;
        public float intensity = 1f;
        [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public LightType type;
        public float range;
    }
}
