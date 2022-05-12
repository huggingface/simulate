// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Settings/ShaderSettings.cs
using UnityEngine;
using System;

namespace SimEnv.GLTF {
    [Serializable]
    public class ShaderSettings {
        [SerializeField] Shader metallic;
        public Shader Metallic => metallic != null ? metallic : GetDefaultMetallic();

        [SerializeField] Shader specular;
        public Shader Specular => specular != null ? specular : GetDefaultSpecular();

        public void CacheDefaultShaders() {
            metallic = Metallic;
            specular = Specular;
        }

        public Shader GetDefaultMetallic() {
            return Shader.Find("Standard");
        }

        public Shader GetDefaultSpecular() {
            return Shader.Find("Specular");
        }
    }
}