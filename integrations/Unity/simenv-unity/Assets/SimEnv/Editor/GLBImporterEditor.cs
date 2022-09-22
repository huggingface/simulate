using UnityEditor.AssetImporters;
using UnityEngine;

namespace Simulate.GLTF {
    [ScriptedImporter(1, "glb", importQueueOffset: 3000)]
    public class GLBImporterEditor : GLTFImporterEditor {
        public override void OnImportAsset(AssetImportContext ctx) {
            AnimationClip[] animations;
            if(importSettings == null)
                importSettings = new ImportSettings();
            GameObject root =Importer.LoadFromFile(ctx.assetPath, importSettings, out animations, Format.GLB);
            GLTFAssetUtility.SaveToAsset(root, animations, ctx, importSettings);
        }
    }
}