using UnityEditor;
using UnityEditor.AssetImporters;
using UnityEngine;

[ScriptedImporter(1, "glb")]
public class GLBImporterEditor : GLTFImporterEditor
{
    public override void OnImportAsset(AssetImportContext ctx) {
        AnimationClip[] animations;
        if(importSettings == null)
            importSettings = new ImportSettings();
        GameObject root = Importer.LoadFromFile(ctx.assetPath, importSettings, out animations, Format.GLB);
        GLTFAssetUtility.SaveToAsset(root, animations, ctx, importSettings);
    }
}
