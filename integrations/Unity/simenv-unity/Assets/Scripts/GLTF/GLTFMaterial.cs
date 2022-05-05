// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFMaterial.cs
using UnityEngine;
using Newtonsoft.Json;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

public class GLTFMaterial
{
    static Material _defaultMaterial;
#if UNITY_EDITOR
    public static Material defaultMaterial {
        get {
            if(_defaultMaterial == null) {
                GameObject primitive = GameObject.CreatePrimitive(PrimitiveType.Cube);
                primitive.SetActive(false);
                _defaultMaterial = primitive.GetComponent<MeshRenderer>().sharedMaterial;
                GameObject.DestroyImmediate(primitive);
            }
            return _defaultMaterial;
        }
    }
#else
    public static Material defaultMaterial => null;
#endif

    public string name;
    public PbrMetallicRoughness pbrMetallicRoughness;
    public TextureInfo normalTexture;
    public TextureInfo occlusionTexture;
    public TextureInfo emissiveTexture;
    [JsonConverter(typeof(ColorRGBConverter))] public Color emissiveFactor = Color.black;
    [JsonConverter(typeof(EnumConverter))] public AlphaMode alphaMode = AlphaMode.OPAQUE;
    public float alphaCutoff = .5f;
    public bool doubleSided = false;
    public Extensions extensions;

    public bool ShouldSerializeemissiveFactor() { return emissiveFactor != Color.black; }
    public bool ShouldSerializealphaMode() { return alphaMode != AlphaMode.OPAQUE; }
    public bool ShouldSerializealphaCutoff() { return alphaCutoff != .5f; }
    public bool ShouldSerializedoubleSided() { return doubleSided; }

    public class ImportResult
    {
        public Material material;
    }

    public class Extensions
    {
        public PbrSpecularGlossiness KHR_materials_pbrSpecularGlossiness = null;
    }

    public IEnumerator CreateMaterial(GLTFTexture.ImportResult[] textures, ShaderSettings shaderSettings, Action<Material> onFinish) {
        Material mat = null;
        IEnumerator coroutine = null;
        if(pbrMetallicRoughness != null) {
            coroutine = pbrMetallicRoughness.CreateMaterial(textures, alphaMode, shaderSettings, x => mat = x);
            while(coroutine.MoveNext())
                yield return null;
        } else {
            mat = new Material(Shader.Find("Standard"));
        }
        if(normalTexture != null) {
            coroutine = TryGetTexture(textures, normalTexture, true, tex => {
                if(tex != null) {
                    mat.SetTexture("_BumpMap", tex);
                    mat.EnableKeyword("_NORMALMAP");
                    mat.SetFloat("_BumpScale", normalTexture.scale);
                }
            });
            while(coroutine.MoveNext())
                yield return null;
        }
        if(occlusionTexture != null) {
            coroutine = TryGetTexture(textures, occlusionTexture, true, tex => {
                if(tex != null)
                    mat.SetTexture("_OcclusionMap", tex);
            });
            while(coroutine.MoveNext())
                yield return null;
        }
        if(emissiveFactor != Color.black) {
            mat.SetColor("_EmissionColor", emissiveFactor);
            mat.EnableKeyword("_EMISSION");
        }
        if(emissiveTexture != null) {
            coroutine = TryGetTexture(textures, emissiveTexture, false, tex => {
                if(tex != null) {
                    mat.SetTexture("_EmissionMap", tex);
                    mat.EnableKeyword("_EMISSION");
                }
            });
            while(coroutine.MoveNext())
                yield return null;
        }
        if(alphaMode == AlphaMode.MASK)
            mat.SetFloat("_AlphaCutoff", alphaCutoff);
        mat.name = name;
        onFinish(mat);
    }

    public static IEnumerator TryGetTexture(GLTFTexture.ImportResult[] textures, TextureInfo texture, bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
        if(texture == null || texture.index < 0 || textures == null) {
            if(onProgress != null)
                onProgress(1f);
            onFinish(null);
        }
        if(textures.Length <= texture.index) {
            Debug.LogWarning("No texture at index " + texture.index);
            if(onProgress != null)
                onProgress(1f);
            onFinish(null);
        }
        IEnumerator coroutine = textures[texture.index].GetTextureCached(linear, onFinish, onProgress);
        while(coroutine.MoveNext())
            yield return null;
    }

    public class PbrMetallicRoughness
    {
        [JsonConverter(typeof(ColorRGBAConverter))] public Color baseColorFactor = Color.white;
        public TextureInfo baseColorTexture;
        public float metallicFactor;
        public float roughnessFactor;
        public TextureInfo metallicRoughnessTexture;

        public bool ShouldSerializebaseColorFactor() { return baseColorFactor != Color.white; }
        public bool ShouldSerializemetallicFactor() { return metallicFactor != 0f; }
        public bool ShouldSerializeroughnessFactor() { return roughnessFactor != 0f; }

        public IEnumerator CreateMaterial(GLTFTexture.ImportResult[] textures, AlphaMode alphaMode, ShaderSettings shaderSettings, Action<Material> onFinish) {
            Shader sh = null;
            if(alphaMode == AlphaMode.BLEND)
                sh = shaderSettings.MetallicBlend;
            else
                sh = shaderSettings.Metallic;
            
            Material mat = new Material(sh);
            mat.color = baseColorFactor;
            mat.SetFloat("_Metallic", metallicFactor);
            mat.SetFloat("_Roughness", roughnessFactor);

            if(textures != null) {
                if(baseColorTexture != null && baseColorTexture.index >= 0) {
                    if(textures.Length <= baseColorTexture.index) {
                        Debug.LogWarning("Texture index error");
                    } else {
                        IEnumerator coroutine = textures[baseColorTexture.index].GetTextureCached(false, tex => {
                            if(tex != null)
                                mat.SetTexture("_MainTex", tex);
                        });
                        while(coroutine.MoveNext())
                            yield return null;
                    }
                }
            }
            if(metallicRoughnessTexture != null && metallicRoughnessTexture.index >= 0) {
                if(textures.Length <= metallicRoughnessTexture.index) {
                    Debug.LogWarning("Metallic texture index error");
                } else {
                    IEnumerator coroutine = TryGetTexture(textures, metallicRoughnessTexture, true, tex => {
                        if(tex != null) {
                            mat.SetTexture("_MetallicGlossMap", tex);
                            mat.EnableKeyword("_METALLICGLOSSMAP");
                        }
                    });
                    while(coroutine.MoveNext())
                        yield return null;
                }
            }

            if(mat.HasProperty("_BaseMap"))
                mat.SetTexture("_BaseMap", mat.mainTexture);
            if(mat.HasProperty("_BaseColor"))
                mat.SetColor("_BaseColor", baseColorFactor);
            onFinish(mat);
        }
    }

    public class PbrSpecularGlossiness
    {
        [JsonConverter(typeof(ColorRGBAConverter))] public Color diffuseFactor = Color.white;
        public TextureInfo diffuseTexture;
        [JsonConverter(typeof(ColorRGBConverter))] public Color specularFactor = Color.white;
        public float glossinessFactor = 1f;
        public TextureInfo specularGlossinessTexture;

        public IEnumerator CreateMaterial(GLTFTexture.ImportResult[] textures, AlphaMode alphaMode, ShaderSettings shaderSettings, Action<Material> onFinish) {
            Shader sh = null;
            if(alphaMode == AlphaMode.BLEND)
                sh = shaderSettings.SpecularBlend;
            else
                sh = shaderSettings.Specular;

            Material mat = new Material(sh);
            mat.color = diffuseFactor;
            mat.SetColor("_SpecColor", specularFactor);
            mat.SetFloat("_GlossyReflections", glossinessFactor);

            if(textures != null) {
                if(diffuseTexture != null) {
                    if(textures.Length <= diffuseTexture.index) {
                        Debug.LogWarning("Failed to get diffuse texture at index");
                    } else {
                        IEnumerator coroutine = textures[diffuseTexture.index].GetTextureCached(false, tex => {
                            if(tex != null) {
                                mat.SetTexture("_MainTex", tex);
                                if(diffuseTexture.extensions != null)
                                    diffuseTexture.extensions.Apply(diffuseTexture, mat, "_MainTex");
                            }
                        });
                        while(coroutine.MoveNext()) yield return null;
                    }
                }
                if(specularGlossinessTexture != null) {
                    if(textures.Length <= specularGlossinessTexture.index) {
                        Debug.LogWarning("Failed to get specular glossiness texture at index");
                    } else {
                        mat.EnableKeyword("_SPECGLOSSMAP");
                        IEnumerator coroutine = textures[specularGlossinessTexture.index].GetTextureCached(false, tex => {
                            if(tex != null) {
                                mat.SetTexture("_SpecGlossMap", tex);
                                mat.EnableKeyword("_SPECGLOSSMAP");
                                if(specularGlossinessTexture.extensions != null)
                                    specularGlossinessTexture.extensions.Apply(specularGlossinessTexture, mat, "_SpecGlossMap");
                            }
                        });
                        while(coroutine.MoveNext()) yield return null;
                    }
                }
            }
            onFinish(mat);
        }
    }

    public class TextureInfo
    {
        [JsonProperty(Required = Required.Always)] public int index;
        public int texCoord = 0;
        public float scale = 1;
        public Extensions extensions;

        public class Extensions
        {
            public KHR_texture_transform KHR_texture_transform;

            public void Apply(GLTFMaterial.TextureInfo texInfo, Material material, string textureSamplerName) {
                if(KHR_texture_transform != null)
                    KHR_texture_transform.Apply(texInfo, material, textureSamplerName);
            }
        }

        public interface IExtension
        {
            void Apply(GLTFMaterial.TextureInfo texInfo, Material material, string textureSamplerName);
        }
    }

    public class ImportTask : Importer.ImportTask<ImportResult[]>
    {
        List<GLTFMaterial> materials;
        GLTFTexture.ImportTask textureTask;
        public ImportSettings importSettings;

        public ImportTask(List<GLTFMaterial> materials, GLTFTexture.ImportTask textureTask, ImportSettings importSettings) : base(textureTask) {
            this.materials = materials;
            this.textureTask = textureTask;
            this.importSettings = importSettings;

            task = new Task(() => {
                if(materials == null) return;
                result = new ImportResult[materials.Count];
            });
        }

        public override IEnumerator TaskCoroutine(Action<float> onProgress = null) {
            if(materials == null) {
                if(onProgress != null)
                    onProgress(1f);
                IsCompleted = true;
                yield break;
            }
            for(int i = 0; i < result.Length; i++) {
                result[i] = new ImportResult();
                IEnumerator coroutine = materials[i].CreateMaterial(textureTask.result, importSettings.shaderOverrides, x => result[i].material = x);
                while(coroutine.MoveNext())
                    yield return null;
                if(result[i].material.name == null)
                    result[i].material.name = "material" + i;
                yield return null;
            }
            IsCompleted = true;
        }
    }

    public class ExportResult : GLTFMaterial
    {
        [JsonIgnore] public Material material;
        [JsonIgnore] public int index;
    }

    public static List<ExportResult> Export(List<GLTFMesh.ExportResult> meshes) {
        Dictionary<Material, ExportResult> results = new Dictionary<Material, ExportResult>();
        for(int i = 0; i < meshes.Count; i++) {
            if(meshes[i].node.renderer != null && meshes[i].node.renderer.sharedMaterial != null) {
                Material material = meshes[i].node.renderer.sharedMaterial;
                ExportResult result;
                if(!results.TryGetValue(material, out result)) {
                    result = new ExportResult() {
                        material = material,
                        index = results.Count
                    };
                    results.Add(material, result);
                }
                for(int j = 0; j < meshes[i].primitives.Count; j++)
                    meshes[i].primitives[j].material = result.index;
            }
        }
        return results.Values.OrderBy(x => x.index).ToList();
    }
}
