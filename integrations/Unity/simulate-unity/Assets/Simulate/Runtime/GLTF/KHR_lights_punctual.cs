using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace Simulate.GLTF {
    public class KHRLightsPunctual {
        public List<GLTFLight> lights;

        public KHRLightsPunctual() {
            lights = new List<GLTFLight>();
        }

        public class GLTFLight {
            public string name = "";
            [JsonConverter(typeof(ColorRGBConverter))] public Color color = Color.white;
            public float intensity = 1f;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public LightType type;
            public float range;

            public override int GetHashCode() {
                return name.GetHashCode()
                    ^ color.GetHashCode()
                    ^ intensity.GetHashCode()
                    ^ type.GetHashCode()
                    ^ range.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFLight)) return false;
                GLTFLight other = obj as GLTFLight;
                if (name == other.name
                    && color == other.color
                    && intensity == other.intensity
                    && type == other.type
                    && range == other.range)
                    return true;
                return false;
            }
        }

        public static void Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            List<GLTFLight> lights = new List<GLTFLight>();
            foreach (GLTFNode.ExportResult node in nodes) {
                GLTFLight light = Export(node);
                if (light == null) continue;
                node.rotation *= Quaternion.Euler(0, 180, 0);
                if (!lights.Contains(light))
                    lights.Add(light);
                node.extensions ??= new GLTFNode.Extensions();
                node.extensions.KHR_lights_punctual = new GLTFNode.KHRLight() { light = lights.IndexOf(light) };
            }
            if (lights.Count == 0) return;
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("KHR_lights_punctual");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.KHR_lights_punctual ??= new KHRLightsPunctual();
            gltfObject.extensions.KHR_lights_punctual.lights.AddRange(lights);
        }

        static GLTFLight Export(GLTFNode.ExportResult node) {
            Light[] lights = node.transform.GetComponents<Light>();
            if (lights.Length == 0)
                return null;
            else if (lights.Length > 1)
                Debug.LogWarning($"Node {node.name} has multiple lights. Ignoring extras.");
            Light light = lights[0];
            GLTFLight gltfLight = new GLTFLight();
            switch (light.type) {
                case UnityEngine.LightType.Directional:
                    gltfLight.type = LightType.directional;
                    break;
                case UnityEngine.LightType.Point:
                    gltfLight.type = LightType.point;
                    break;
                case UnityEngine.LightType.Spot:
                    gltfLight.type = LightType.spot;
                    break;
                default:
                    Debug.LogWarning($"Light type {light.type} not implemented.");
                    return null;
            }
            gltfLight.name = light.name;
            gltfLight.intensity = light.intensity;
            gltfLight.range = light.range;
            gltfLight.color = light.color;
            return gltfLight;
        }
    }
}