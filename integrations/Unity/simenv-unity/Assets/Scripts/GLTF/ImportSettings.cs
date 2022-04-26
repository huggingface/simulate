// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Settings/ImportSettings.cs
using UnityEngine;
using System;

[Serializable]
public class ImportSettings
{
    public bool materials = true;
    public ShaderSettings shaderOverrides = new ShaderSettings();
    public AnimationSettings animationSettings = new AnimationSettings();
    public bool generateLightmapUVs;
    [Range(0, 180)] public float hardAngle = 88;
    [Range(1, 75)] public float angleError = 8;
    [Range(1, 75)] public float areaError = 15;
    [Range(1, 64)] public float packMargin = 4;
}
