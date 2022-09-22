// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Settings/AnimationSettings.cs
using System;

namespace Simulate.GLTF {
    [Serializable]
    public class AnimationSettings {
        public bool looping;
        public float frameRate = 24;
        public InterpolationMode interpolationMode = InterpolationMode.ImportFromFile;
        public bool compressBlendShapeKeyFrames = true;
    }
}