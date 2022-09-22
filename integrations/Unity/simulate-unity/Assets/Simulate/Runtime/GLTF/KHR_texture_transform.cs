// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Extensions/KHR_texture_transform.cs
using UnityEngine;
using Newtonsoft.Json;

namespace Simulate.GLTF {
    public class KHR_texture_transform {
        [JsonConverter(typeof(Vector2Converter))] public Vector2 offset = Vector2.zero;
        public float rotation;
        [JsonConverter(typeof(Vector2Converter))] public Vector2 scale = Vector2.one;
        public int texCoord = 0;

        public void Apply(GLTFMaterial.TextureInfo texInfo, Material material, string textureSamplerName) {
            material.SetTextureOffset(textureSamplerName, offset);
            material.SetTextureScale(textureSamplerName, scale);
        }
    }
}