// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Settings/ShaderSettings.cs
using UnityEngine;
using System;

[Serializable]
public class ShaderSettings
{
    [SerializeField] Shader metallic;
    public Shader Metallic => metallic != null ? metallic : GetDefaultMetallic();

    [SerializeField] Shader metallicBlend;
    public Shader MetallicBlend => metallicBlend != null ? metallicBlend : GetDefaultMetallicBlend();

    [SerializeField] Shader specular;
    public Shader Specular => specular != null ? specular : GetDefaultSpecular();

    [SerializeField] Shader specularBlend;
    public Shader SpecularBlend => specularBlend != null ? specularBlend : GetDefaultSpecularBlend();

    public void CacheDefaultShaders() {
        metallic = Metallic;
        metallicBlend = MetallicBlend;
        specular = Specular;
        specularBlend = SpecularBlend;
    }

    public Shader GetDefaultMetallic() {
        return Shader.Find("GLTF/URP/Standard (Metallic)");
    }

    public Shader GetDefaultMetallicBlend() {
        return Shader.Find("GLTF/URP/Standard Transparent (Metallic)");
    }

    public Shader GetDefaultSpecular() {
        return Shader.Find("GLTF/URP/Standard (Specular)");
    }

    public Shader GetDefaultSpecularBlend() {
        return Shader.Find("GLTF/URP/Standard Transparent (Specular)");
    }
}
