using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Simulate.GLTF;
using UnityEngine;

namespace Simulate {
    public class Config {
        static Config m_instance;
        public static Config instance {
            get {
                if (m_instance == null)
                    m_instance = new Config();
                return m_instance;
            }
        }

        [JsonProperty(PropertyName = "time_step")] public float timeStep = .02f;
        [JsonProperty(PropertyName = "frame_skip")] public int frameSkip = 1;
        [JsonProperty(PropertyName = "return_nodes")] public bool returnNodes = true;
        [JsonProperty(PropertyName = "return_frames")] public bool returnFrames = true;
        [JsonProperty(PropertyName = "node_filter")] public List<string> nodeFilter;
        [JsonProperty(PropertyName = "camera_filter")] public List<string> cameraFilter;
        [JsonProperty(PropertyName = "ambient_color"), JsonConverter(typeof(ColorRGBConverter))] public Color ambientColor = Color.gray;
        [JsonConverter(typeof(Vector3Converter))] public Vector3 gravity = Vector3.down * 9.81f;

        public bool ShouldSerializetimeStep() => timeStep != .02f;
        public bool ShouldSerializeframeSkip() => frameSkip != 1;
        public bool ShouldSerializereturnNodes() => !returnNodes;
        public bool ShouldSerializereturnFrames() => !returnFrames;
        public bool ShouldSerializenodeFilter() => nodeFilter != null && nodeFilter.Count > 0;
        public bool ShouldSerializecameraFilter() => cameraFilter != null && cameraFilter.Count > 0;
        public bool ShouldSerializeambientColor() => ambientColor != Color.gray;
        public bool ShouldSerializegravity() => gravity != Vector3.down * 9.81f;

        static JObject cached;

        public Config() {
            m_instance = this;
        }

        public void Parse(Dictionary<string, object> kwargs) {
            kwargs.TryParse<float>("time_step", out timeStep, timeStep);
            kwargs.TryParse<int>("frame_skip", out frameSkip, frameSkip);
            kwargs.TryParse<bool>("return_nodes", out returnNodes, returnNodes);
            kwargs.TryParse<bool>("return_frames", out returnFrames, returnFrames);
            kwargs.TryParse<List<string>>("node_filter", out nodeFilter, nodeFilter);
            kwargs.TryParse<List<string>>("camera_filter", out cameraFilter, cameraFilter);
            kwargs.TryParse<float[]>("ambient_color", out float[] ambientColorBuffer,
                new float[] { ambientColor.r, ambientColor.g, ambientColor.b });
            ambientColor = new Color(ambientColorBuffer[0], ambientColorBuffer[1], ambientColorBuffer[2]);
            kwargs.TryParse<Vector3>("gravity", out gravity, gravity);
        }

        public static void Cache() {
            cached = JObject.FromObject(instance);
        }

        public static void Restore() {
            if (cached == null) return;
            m_instance = cached.ToObject<Config>();
        }

        public static void Export(GLTFObject gltfObject) {
            instance.ambientColor = RenderSettings.ambientLight;
            instance.gravity = Physics.gravity;
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("HF_config");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_config = instance;
        }

        public static void Apply() {
            RenderSettings.ambientLight = instance.ambientColor;
            Physics.gravity = instance.gravity;
            Time.fixedDeltaTime = instance.timeStep;
        }
    }
}