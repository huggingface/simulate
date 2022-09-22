// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFAsset.cs
using Newtonsoft.Json;

namespace Simulate.GLTF {
    public class GLTFAsset {
        public string copyright;
        public string generator;
        [JsonProperty(Required = Required.Always)] public string version;
        public string minVersion;
    }
}