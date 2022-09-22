// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Editor/GLTFAssetUtility.cs
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.AssetImporters;

namespace Simulate.GLTF {
    public static class GLTFAssetUtility {
        public static void SaveToAsset(GameObject root, AnimationClip[] animations, AssetImportContext ctx, ImportSettings settings) {
            settings ??= new ImportSettings();
            ctx.AddObjectToAsset("main", root);
            ctx.SetMainObject(root);
            UnwrapParam? unwrapParams = new UnwrapParam() {
                angleError = settings.angleError,
                areaError = settings.areaError,
                hardAngle = settings.hardAngle,
                packMargin = settings.packMargin
            };

            MeshRenderer[] renderers = root.GetComponentsInChildren<MeshRenderer>(true);
            SkinnedMeshRenderer[] skinnedRenderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            MeshCollider[] meshColliders = root.GetComponentsInChildren<MeshCollider>(true);
            MeshFilter[] filters = root.GetComponentsInChildren<MeshFilter>(true);
            Collider[] colliders = root.GetComponentsInChildren<Collider>(true);
            AddMeshes(filters, skinnedRenderers, meshColliders, ctx, settings.generateLightmapUVs ? unwrapParams : null);
            AddMaterials(renderers, skinnedRenderers, ctx);
            AddAnimations(animations, ctx, settings.animationSettings);
            AddColliders(colliders, ctx);
        }

        public static void AddMeshes(MeshFilter[] filters, SkinnedMeshRenderer[] skinnedRenderers, MeshCollider[] meshColliders,
            AssetImportContext ctx, UnwrapParam? lightmapUnwrapInfo) {
            HashSet<Mesh> visitedMeshes = new HashSet<Mesh>();
            for (int i = 0; i < filters.Length; i++) {
                Mesh mesh = filters[i].sharedMesh;
                if (lightmapUnwrapInfo.HasValue) Unwrapping.GenerateSecondaryUVSet(mesh, lightmapUnwrapInfo.Value);
                if (visitedMeshes.Contains(mesh)) continue;
                ctx.AddObjectToAsset(mesh.name, mesh);
                visitedMeshes.Add(mesh);
            }
            for (int i = 0; i < skinnedRenderers.Length; i++) {
                Mesh mesh = skinnedRenderers[i].sharedMesh;
                if (visitedMeshes.Contains(mesh)) continue;
                ctx.AddObjectToAsset(mesh.name, mesh);
                visitedMeshes.Add(mesh);
            }
            for (int i = 0; i < meshColliders.Length; i++) {
                Mesh mesh = meshColliders[i].sharedMesh;
                if (visitedMeshes.Contains(mesh)) continue;
                ctx.AddObjectToAsset(mesh.name, mesh);
                visitedMeshes.Add(mesh);
            }
        }

        public static void AddAnimations(AnimationClip[] animations, AssetImportContext ctx, AnimationSettings settings) {
            if (animations == null) return;

            foreach (AnimationClip clip in animations) {
                AnimationClipSettings clipSettings = AnimationUtility.GetAnimationClipSettings(clip);
                clipSettings.loopTime = settings.looping;
                AnimationUtility.SetAnimationClipSettings(clip, clipSettings);
            }

            HashSet<AnimationClip> visitedAnimations = new HashSet<AnimationClip>();
            for (int i = 0; i < animations.Length; i++) {
                AnimationClip clip = animations[i];
                if (visitedAnimations.Contains(clip)) continue;
                ctx.AddObjectToAsset(clip.name, clip);
                visitedAnimations.Add(clip);
            }
        }

        public static void AddMaterials(MeshRenderer[] renderers, SkinnedMeshRenderer[] skinnedRenderers, AssetImportContext ctx) {
            HashSet<Material> visitedMaterials = new HashSet<Material>();
            HashSet<Texture2D> visitedTextures = new HashSet<Texture2D>();
            for (int i = 0; i < renderers.Length; i++) {
                foreach (Material mat in renderers[i].sharedMaterials) {
                    if (mat == GLTFMaterial.defaultMaterial) continue;
                    if (visitedMaterials.Contains(mat)) continue;
                    if (string.IsNullOrEmpty(mat.name)) mat.name = "material" + visitedMaterials.Count;
                    ctx.AddObjectToAsset(mat.name, mat);
                    visitedMaterials.Add(mat);

                    foreach (Texture2D tex in mat.AllTextures()) {
                        if (visitedTextures.Contains(tex)) continue;
                        if (AssetDatabase.Contains(tex)) continue;
                        if (string.IsNullOrEmpty(tex.name)) tex.name = "texture" + visitedTextures.Count;
                        ctx.AddObjectToAsset(tex.name, tex);
                        visitedTextures.Add(tex);
                    }
                }
            }
            for (int i = 0; i < skinnedRenderers.Length; i++) {
                foreach (Material mat in skinnedRenderers[i].sharedMaterials) {
                    if (visitedMaterials.Contains(mat)) continue;
                    if (string.IsNullOrEmpty(mat.name)) mat.name = "material" + visitedMaterials.Count;
                    ctx.AddObjectToAsset(mat.name, mat);
                    visitedMaterials.Add(mat);

                    foreach (Texture2D tex in mat.AllTextures()) {
                        if (visitedTextures.Contains(tex)) continue;
                        if (AssetDatabase.Contains(tex)) continue;
                        if (string.IsNullOrEmpty(tex.name)) tex.name = "texture" + visitedTextures.Count;
                        ctx.AddObjectToAsset(tex.name, tex);
                        visitedTextures.Add(tex);
                    }
                }
            }
        }

        public static void AddColliders(Collider[] colliders, AssetImportContext ctx) {
            HashSet<PhysicMaterial> visitedMaterials = new HashSet<PhysicMaterial>();
            foreach(Collider collider in colliders) {
                PhysicMaterial material = collider.sharedMaterial;
                if(material == null || visitedMaterials.Contains(material)) continue;
                ctx.AddObjectToAsset(material.name, material);
                visitedMaterials.Add(material);
            }
        }

        public static IEnumerable<Texture2D> AllTextures(this Material mat) {
            int[] ids = mat.GetTexturePropertyNameIDs();
            for (int i = 0; i < ids.Length; i++) {
                Texture2D tex = mat.GetTexture(ids[i]) as Texture2D;
                if (tex != null) yield return tex;
            }
        }
    }
}