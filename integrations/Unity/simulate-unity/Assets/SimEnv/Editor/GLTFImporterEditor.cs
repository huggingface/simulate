// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Editor/GLTFImporter.cs
using UnityEngine;
using UnityEditor.AssetImporters;

namespace Simulate.GLTF {
    [ScriptedImporter(1, "gltf", importQueueOffset: 3000)]
    public class GLTFImporterEditor : ScriptedImporter {
        public ImportSettings importSettings;

        public override void OnImportAsset(AssetImportContext ctx) {
            AnimationClip[] animations;
            GameObject root = Importer.LoadFromFile(ctx.assetPath, importSettings, out animations);
            GLTFAssetUtility.SaveToAsset(root, animations, ctx, importSettings);
        }
    }
}