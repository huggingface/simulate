// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFMaterial.cs
using UnityEngine;
using Newtonsoft.Json;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

namespace Simulate.GLTF {
    public class GLTFMaterial {
        static Material _defaultMaterial;
#if UNITY_EDITOR
        public static Material defaultMaterial {
            get {
                if (_defaultMaterial == null)
                    _defaultMaterial = Resources.Load<Material>("DefaultLit");
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

        public class ImportResult {
            public Material material;
        }

        public class Extensions {
            public PbrSpecularGlossiness KHR_materials_pbrSpecularGlossiness = null;
        }

        public IEnumerator CreateMaterial(GLTFTexture.ImportResult[] textures, Action<Material> onFinish) {
            bool emissive = emissiveFactor != Color.black;
            Material mat = CreateMaterial(alphaMode, emissive);
            mat.name = name;

            IEnumerator coroutine = null;
            if (pbrMetallicRoughness != null) {
                coroutine = pbrMetallicRoughness.InitializeMaterial(mat, textures, x => mat = x);
                while (coroutine.MoveNext())
                    yield return null;
            }
            if (extensions != null && extensions.KHR_materials_pbrSpecularGlossiness != null) {
                coroutine = extensions.KHR_materials_pbrSpecularGlossiness.InitializeMaterial(mat, textures, x => mat = x);
                while (coroutine.MoveNext())
                    yield return null;
            }
            if (normalTexture != null) {
                coroutine = TryGetTexture(textures, normalTexture, true, tex => {
                    if (tex != null) {
                        mat.SetTexture("_BumpMap", tex);
                        mat.EnableKeyword("_NORMALMAP");
                        mat.SetFloat("_BumpScale", normalTexture.scale);
                    }
                });
                while (coroutine.MoveNext())
                    yield return null;
            }
            if (occlusionTexture != null) {
                coroutine = TryGetTexture(textures, occlusionTexture, true, tex => {
                    if (tex != null) {
                        mat.SetTexture("_OcclusionMap", tex);
                        mat.SetFloat("_OcclusionStrength", occlusionTexture.strength);
                    }
                });
                while (coroutine.MoveNext())
                    yield return null;
            }
            if (emissiveFactor != Color.black) {
                mat.SetColor("_EmissionColor", emissiveFactor);
                mat.EnableKeyword("_EMISSION");
            }
            if (emissiveTexture != null) {
                coroutine = TryGetTexture(textures, emissiveTexture, false, tex => {
                    if (tex != null) {
                        mat.SetTexture("_EmissionMap", tex);
                        mat.EnableKeyword("_EMISSION");
                    }
                });
                while (coroutine.MoveNext())
                    yield return null;
            }
            if (alphaMode == AlphaMode.MASK)
                mat.SetFloat("_Cutoff", alphaCutoff);
            onFinish(mat);
        }

        public static IEnumerator TryGetTexture(GLTFTexture.ImportResult[] textures, TextureInfo texture, bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
            if (texture == null || texture.index < 0 || textures == null) {
                if (onProgress != null)
                    onProgress(1f);
                onFinish(null);
            }
            if (textures.Length <= texture.index) {
                Debug.LogWarning("No texture at index " + texture.index);
                if (onProgress != null)
                    onProgress(1f);
                onFinish(null);
            }
            IEnumerator coroutine = textures[texture.index].GetTextureCached(linear, onFinish, onProgress);
            while (coroutine.MoveNext())
                yield return null;
        }

        public class PbrMetallicRoughness {
            [JsonConverter(typeof(ColorRGBAConverter))] public Color baseColorFactor = Color.white;
            public TextureInfo baseColorTexture;
            public float metallicFactor = 1f;
            public float roughnessFactor = 1f;
            public TextureInfo metallicRoughnessTexture;

            public bool ShouldSerializebaseColorFactor() { return baseColorFactor != Color.white; }
            public bool ShouldSerializemetallicFactor() { return metallicFactor != 1f; }
            public bool ShouldSerializeroughnessFactor() { return roughnessFactor != 1f; }

            public IEnumerator InitializeMaterial(Material mat, GLTFTexture.ImportResult[] textures, Action<Material> onFinish) {
                mat.color = baseColorFactor;
                mat.SetFloat("_WorkflowMode", 1f);
                mat.SetFloat("_Metallic", metallicFactor);
                mat.SetFloat("_Smoothness", 1 - roughnessFactor);

                if (textures != null) {
                    if (baseColorTexture != null && baseColorTexture.index >= 0) {
                        if (textures.Length <= baseColorTexture.index) {
                            Debug.LogWarning("Texture index error");
                        } else {
                            IEnumerator coroutine = textures[baseColorTexture.index].GetTextureCached(false, tex => {
                                if (tex != null)
                                    mat.mainTexture = tex;
                            });
                            while (coroutine.MoveNext())
                                yield return null;
                        }
                    }
                }
                if (metallicRoughnessTexture != null && metallicRoughnessTexture.index >= 0) {
                    if (textures.Length <= metallicRoughnessTexture.index) {
                        Debug.LogWarning("Metallic texture index error");
                    } else {
                        IEnumerator coroutine = TryGetTexture(textures, metallicRoughnessTexture, true, tex => {
                            if (tex != null)
                                mat.SetTexture("_MetallicGlossMap", tex);
                        });
                        while (coroutine.MoveNext())
                            yield return null;
                    }
                }

                if (mat.HasProperty("_BaseMap"))
                    mat.SetTexture("_BaseMap", mat.mainTexture);
                if (mat.HasProperty("_BaseColor"))
                    mat.SetColor("_BaseColor", baseColorFactor);
                onFinish(mat);
            }
        }

        public class PbrSpecularGlossiness {
            [JsonConverter(typeof(ColorRGBAConverter))] public Color diffuseFactor = Color.white;
            public TextureInfo diffuseTexture;
            [JsonConverter(typeof(ColorRGBConverter))] public Color specularFactor = Color.white;
            public float glossinessFactor = 1f;
            public TextureInfo specularGlossinessTexture;

            public bool ShouldSerializeglossinessFactor() => glossinessFactor != 1f;

            public IEnumerator InitializeMaterial(Material mat, GLTFTexture.ImportResult[] textures, Action<Material> onFinish) {
                mat.color = diffuseFactor;
                mat.SetFloat("_WorkflowMode", 0f);
                mat.SetColor("_SpecColor", specularFactor);
                mat.SetFloat("_Smoothness", glossinessFactor);

                if (textures != null) {
                    if (diffuseTexture != null) {
                        if (textures.Length <= diffuseTexture.index) {
                            Debug.LogWarning("Failed to get diffuse texture at index");
                        } else {
                            IEnumerator coroutine = textures[diffuseTexture.index].GetTextureCached(false, tex => {
                                if (tex != null) {
                                    mat.mainTexture = tex;
                                    if (diffuseTexture.extensions != null)
                                        diffuseTexture.extensions.Apply(diffuseTexture, mat, "_BaseMap");
                                }
                            });
                            while (coroutine.MoveNext()) yield return null;
                        }
                    }
                    if (specularGlossinessTexture != null) {
                        if (textures.Length <= specularGlossinessTexture.index) {
                            Debug.LogWarning("Failed to get specular glossiness texture at index");
                        } else {
                            IEnumerator coroutine = textures[specularGlossinessTexture.index].GetTextureCached(false, tex => {
                                if (tex != null) {
                                    mat.SetTexture("_SpecGlossMap", tex);
                                    if (specularGlossinessTexture.extensions != null)
                                        specularGlossinessTexture.extensions.Apply(specularGlossinessTexture, mat, "_SpecGlossMap");
                                }
                            });
                            while (coroutine.MoveNext()) yield return null;
                        }
                    }
                }

                if (mat.HasProperty("_BaseMap"))
                    mat.SetTexture("_BaseMap", mat.mainTexture);
                if (mat.HasProperty("_BaseColor"))
                    mat.SetColor("_BaseColor", diffuseFactor);
                onFinish(mat);
            }
        }

        static Material CreateMaterial(AlphaMode alphaMode = AlphaMode.OPAQUE, bool emissive = false) {
            Material mat;
            if (emissive)
                mat = GameObject.Instantiate<Material>(Resources.Load<Material>("DefaultEmissive"));
            else
                mat = GameObject.Instantiate<Material>(Resources.Load<Material>("DefaultLit"));
            if (alphaMode != AlphaMode.OPAQUE) {
                mat.SetFloat("_Surface", 1f);
                if (alphaMode == AlphaMode.MASK)
                    mat.SetFloat("_AlphaClip", 1f);
            }
            return mat;
        }

        public class TextureInfo {
            [JsonProperty(Required = Required.Always)] public int index;
            public int texCoord = 0;
            public float scale = 1;
            public float strength = 1;
            public Extensions extensions;

            public bool ShouldSerializetexCoord() => texCoord != 0;
            public bool ShouldSerializescale() => scale != 1;
            public bool ShouldSerializestrength() => strength != 1;

            public class Extensions {
                public KHR_texture_transform KHR_texture_transform;

                public void Apply(GLTFMaterial.TextureInfo texInfo, Material material, string textureSamplerName) {
                    if (KHR_texture_transform != null)
                        KHR_texture_transform.Apply(texInfo, material, textureSamplerName);
                }
            }

            public interface IExtension {
                void Apply(GLTFMaterial.TextureInfo texInfo, Material material, string textureSamplerName);
            }
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            List<GLTFMaterial> materials;
            GLTFTexture.ImportTask textureTask;
            public ImportSettings importSettings;

            public ImportTask(List<GLTFMaterial> materials, GLTFTexture.ImportTask textureTask, ImportSettings importSettings) : base(textureTask) {
                this.materials = materials;
                this.textureTask = textureTask;
                this.importSettings = importSettings;

                task = new Task(() => {
                    if (materials == null) return;
                    result = new ImportResult[materials.Count];
                });
            }

            public override IEnumerator TaskCoroutine(Action<float> onProgress = null) {
                if (materials == null) {
                    if (onProgress != null)
                        onProgress(1f);
                    IsCompleted = true;
                    yield break;
                }
                for (int i = 0; i < result.Length; i++) {
                    result[i] = new ImportResult();
                    IEnumerator coroutine = materials[i].CreateMaterial(textureTask.result, x => result[i].material = x);
                    while (coroutine.MoveNext())
                        yield return null;
                    if (result[i].material.name == null)
                        result[i].material.name = "material" + i;
                    yield return null;
                }
                IsCompleted = true;
            }
        }

        public class ExportResult : GLTFMaterial {
            [JsonIgnore] public int index;
        }

        public static List<GLTFMaterial.ExportResult> Export(GLTFObject gltfObject, Dictionary<string, GLTFImage.ExportResult> images,
                                                             List<GLTFMesh.ExportResult> meshes, string filepath) {
            gltfObject.materials = new List<GLTFMaterial>();
            Dictionary<Material, ExportResult> results = new Dictionary<Material, ExportResult>();
            for (int i = 0; i < meshes.Count; i++) {
                if (meshes[i].node.renderer != null && meshes[i].node.renderer.sharedMaterials != null) {
                    for (int j = 0; j < meshes[i].node.renderer.sharedMaterials.Length; j++) {
                        try {
                            Material material = meshes[i].node.renderer.sharedMaterials[j];
                            ExportResult result;
                            if (!results.TryGetValue(material, out result)) {
                                result = Export(material, images, filepath);
                                result.index = results.Count;
                                results.Add(material, result);
                            }
                            meshes[i].primitives[j].material = result.index;
                        } catch (Exception) {
                            Debug.LogWarning("Failed to exported material: " + meshes[i].node.renderer.sharedMaterials[j].name);
                        }
                    }
                }
            }
            gltfObject.materials = results.Values.Cast<GLTFMaterial>().ToList();
            return results.Values.OrderBy(x => x.index).ToList();
        }

        public static ExportResult Export(Material material, Dictionary<string, GLTFImage.ExportResult> images, string filepath) {
            ExportResult result = new ExportResult();
            result.name = material.name;
            GLTFMaterial.PbrMetallicRoughness pbrMetallicRoughness = new GLTFMaterial.PbrMetallicRoughness();
            if (material.HasProperty("_Surface")) {
                bool transparent = material.GetFloat("_Surface") > 0;
                if (transparent) {
                    if (material.HasProperty("_AlphaClip") && material.GetFloat("_AlphaClip") > 0) {
                        result.alphaMode = AlphaMode.MASK;
                        if (material.HasProperty("_Cutoff"))
                            result.alphaCutoff = material.GetFloat("_Cutoff");
                    } else {
                        result.alphaMode = AlphaMode.BLEND;
                    }
                } else {
                    result.alphaMode = AlphaMode.OPAQUE;
                }
            }
            if (material.HasProperty("_Color")) {
                pbrMetallicRoughness.baseColorFactor = material.color;
            }
            if (material.HasProperty("_MainTex") && material.mainTexture != null) {
                pbrMetallicRoughness.baseColorTexture = GLTFTexture.Export((Texture2D)material.mainTexture, images, filepath);
            }
            if (material.HasProperty("_MetallicGlossMap")) {
                Texture metallicGlossMap = material.GetTexture("_MetallicGlossMap");
                if (metallicGlossMap != null)
                    pbrMetallicRoughness.metallicRoughnessTexture = GLTFTexture.Export((Texture2D)metallicGlossMap, images, filepath);
            }
            if (material.HasProperty("_Metallic")) {
                pbrMetallicRoughness.metallicFactor = material.GetFloat("_Metallic");
            }
            if (material.HasProperty("_Smoothness")) {
                pbrMetallicRoughness.roughnessFactor = 1 - material.GetFloat("_Smoothness");
            }
            if (material.IsKeywordEnabled("_EMISSION")) {
                Color emissionColor = material.GetColor("_EmissionColor");
                if (emissionColor != null)
                    result.emissiveFactor = emissionColor;
                Texture emissionMap = material.GetTexture("_EmissionMap");
                if (emissionMap != null)
                    result.emissiveTexture = GLTFTexture.Export((Texture2D)emissionMap, images, filepath);
            }
            if (material.HasTexture("_OcclusionMap")) {
                Texture occlusionMap = material.GetTexture("_OcclusionMap");
                if (occlusionMap != null) {
                    result.occlusionTexture = GLTFTexture.Export((Texture2D)occlusionMap, images, filepath);
                    if (material.HasProperty("_OcclusionStrength"))
                        result.occlusionTexture.strength = material.GetFloat("_OcclusionStrength");
                }
            }
            if (material.IsKeywordEnabled("_NORMALMAP")) {
                Texture bumpMap = material.GetTexture("_BumpMap");
                if (bumpMap != null) {
                    result.normalTexture = GLTFTexture.Export((Texture2D)bumpMap, images, filepath);
                    if (material.HasProperty("_BumpScale"))
                        result.normalTexture.scale = material.GetFloat("_BumpScale");
                }
            }
            result.pbrMetallicRoughness = pbrMetallicRoughness;
            return result;
        }
    }
}