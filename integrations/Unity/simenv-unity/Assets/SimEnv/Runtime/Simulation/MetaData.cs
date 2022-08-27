using System.Collections.Generic;
using Newtonsoft.Json;
using SimEnv.GLTF;
using UnityEngine;

namespace SimEnv {
    public class MetaData {
        static MetaData m_instance;
        public static MetaData instance {
            get {
                if (m_instance == null)
                    m_instance = new MetaData();
                return m_instance;
            }
        }

        public int frameRate = 30;
        public int frameSkip = 1;
        public bool returnNodes = true;
        public bool returnFrames = true;
        public List<string> nodeFilter;
        public List<string> cameraFilter;
        [JsonConverter(typeof(ColorRGBConverter))] public Color ambientColor = Color.gray;

        public bool ShouldSerializeframeRate() => frameRate != 30;
        public bool ShouldSerializeframeSkip() => frameSkip != 1;
        public bool ShouldSerializereturnNodes() => !returnNodes;
        public bool ShouldSerializereturnFrames() => !returnFrames;
        public bool ShouldSerializenodeFilter() => nodeFilter != null && nodeFilter.Count > 0;
        public bool ShouldSerializecameraFilter() => cameraFilter != null && cameraFilter.Count > 0;
        public bool ShouldSerializeambientColor() => ambientColor != Color.gray;

        public MetaData() {
            m_instance = this;
        }

        public void Parse(Dictionary<string, object> kwargs) {
            kwargs.TryParse<int>("frame_rate", out frameRate, frameRate);
            kwargs.TryParse<int>("frame_skip", out frameSkip, frameSkip);
            kwargs.TryParse<bool>("return_nodes", out returnNodes, returnNodes);
            kwargs.TryParse<bool>("return_frames", out returnFrames, returnFrames);
            kwargs.TryParse<List<string>>("node_filter", out nodeFilter, nodeFilter);
            kwargs.TryParse<List<string>>("camera_filter", out cameraFilter, cameraFilter);
            kwargs.TryParse<float[]>("ambient_color", out float[] ambientColorBuffer,
                new float[] { ambientColor.r, ambientColor.g, ambientColor.b });
            ambientColor = new Color(ambientColorBuffer[0], ambientColorBuffer[1], ambientColorBuffer[2]);
        }

        public static void Export(GLTFObject gltfObject) {
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("HF_metadata");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_metadata = instance;
        }

        public static void Apply() {
            RenderSettings.ambientLight = instance.ambientColor;
        }
    }
}