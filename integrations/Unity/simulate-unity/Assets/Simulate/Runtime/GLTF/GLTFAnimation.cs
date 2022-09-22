// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFAnimation.cs
using UnityEngine;
using Newtonsoft.Json;
using System.Linq;
using System;
using System.Collections.Generic;

namespace Simulate.GLTF {
    public class GLTFAnimation {
        [JsonProperty(Required = Required.Always)] public Channel[] channels;
        [JsonProperty(Required = Required.Always)] public Sampler[] samplers;
        public string name;

        public class Channel {
            [JsonProperty(Required = Required.Always)] public int sampler;
            [JsonProperty(Required = Required.Always)] public Target target;
        }

        public class Sampler {
            [JsonProperty(Required = Required.Always)] public int input;
            [JsonProperty(Required = Required.Always)] public int output;
            [JsonConverter(typeof(EnumConverter))] public InterpolationMode interpolation = InterpolationMode.LINEAR;
        }

        public class Target {
            public int? node;
            [JsonProperty(Required = Required.Always)] public string path;
        }

        public class ImportResult {
            public AnimationClip clip;
        }

        public ImportResult Import(GLTFAccessor.ImportResult[] accessors, GLTFNode.ImportResult[] nodes, ImportSettings importSettings) {
            bool multiRoots = nodes.Where(x => x.IsRoot).Count() > 1;

            ImportResult result = new ImportResult();
            result.clip = new AnimationClip();
            result.clip.name = name;
            result.clip.frameRate = importSettings.animationSettings.frameRate;

            for (int i = 0; i < channels.Length; i++) {
                Channel channel = channels[i];
                if (samplers.Length <= channel.sampler) {
                    Debug.LogWarning(string.Format("Animation channel at index {0} doesn't exist", channel.sampler));
                    continue;
                }
                Sampler sampler = samplers[channel.sampler];

                InterpolationMode interpolationMode = importSettings.animationSettings.interpolationMode;
                if (interpolationMode == InterpolationMode.ImportFromFile)
                    interpolationMode = sampler.interpolation;
                if (interpolationMode == InterpolationMode.CUBICSPLINE)
                    throw new System.NotImplementedException();

                string relativePath = "";
                GLTFNode.ImportResult node = nodes[channel.target.node.Value];
                while (node != null && !node.IsRoot) {
                    if (string.IsNullOrEmpty(relativePath))
                        relativePath = node.transform.name;
                    else
                        relativePath = node.transform.name + "/" + relativePath;
                    if (node.parent.HasValue)
                        node = nodes[node.parent.Value];
                    else
                        node = null;
                }

                if (multiRoots)
                    relativePath = node.transform.name + "/" + relativePath;

                System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
                float[] keyframeInput = accessors[sampler.input].ReadFloat().ToArray();
                switch (channel.target.path) {
                    case "translation":
                        Vector3[] pos = accessors[sampler.output].ReadVec3().ToArray();
                        AnimationCurve posX = new AnimationCurve();
                        AnimationCurve posY = new AnimationCurve();
                        AnimationCurve posZ = new AnimationCurve();
                        for (int k = 0; k < keyframeInput.Length; k++) {
                            posX.AddKey(CreateKeyframe(k, keyframeInput, pos, x => -x.x, interpolationMode));
                            posY.AddKey(CreateKeyframe(k, keyframeInput, pos, x => x.y, interpolationMode));
                            posZ.AddKey(CreateKeyframe(k, keyframeInput, pos, x => x.z, interpolationMode));
                        }
                        result.clip.SetCurve(relativePath, typeof(Transform), "localPosition.x", posX);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localPosition.y", posY);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localPosition.z", posZ);
                        break;
                    case "rotation":
                        Vector4[] rot = accessors[sampler.output].ReadVec4().ToArray();
                        AnimationCurve rotX = new AnimationCurve();
                        AnimationCurve rotY = new AnimationCurve();
                        AnimationCurve rotZ = new AnimationCurve();
                        AnimationCurve rotW = new AnimationCurve();
                        for (int k = 0; k < keyframeInput.Length; k++) {
                            // The Animation window in Unity shows keyframes incorrectly converted to euler. This is only to deceive you. The quaternions underneath work correctly
                            rotX.AddKey(CreateKeyframe(k, keyframeInput, rot, x => x.x, interpolationMode));
                            rotY.AddKey(CreateKeyframe(k, keyframeInput, rot, x => -x.y, interpolationMode));
                            rotZ.AddKey(CreateKeyframe(k, keyframeInput, rot, x => -x.z, interpolationMode));
                            rotW.AddKey(CreateKeyframe(k, keyframeInput, rot, x => x.w, interpolationMode));
                        }
                        result.clip.SetCurve(relativePath, typeof(Transform), "localRotation.x", rotX);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localRotation.y", rotY);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localRotation.z", rotZ);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localRotation.w", rotW);
                        break;
                    case "scale":
                        Vector3[] scale = accessors[sampler.output].ReadVec3().ToArray();
                        AnimationCurve scaleX = new AnimationCurve();
                        AnimationCurve scaleY = new AnimationCurve();
                        AnimationCurve scaleZ = new AnimationCurve();
                        for (int k = 0; k < keyframeInput.Length; k++) {
                            scaleX.AddKey(CreateKeyframe(k, keyframeInput, scale, x => x.x, interpolationMode));
                            scaleY.AddKey(CreateKeyframe(k, keyframeInput, scale, x => x.y, interpolationMode));
                            scaleZ.AddKey(CreateKeyframe(k, keyframeInput, scale, x => x.z, interpolationMode));
                        }
                        result.clip.SetCurve(relativePath, typeof(Transform), "localScale.x", scaleX);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localScale.y", scaleY);
                        result.clip.SetCurve(relativePath, typeof(Transform), "localScale.z", scaleZ);
                        break;
                    case "weights":
                        GLTFNode.ImportResult skinnedMeshNode = nodes[channel.target.node.Value];
                        SkinnedMeshRenderer skinnedMeshRenderer = skinnedMeshNode.transform.GetComponent<SkinnedMeshRenderer>();

                        int numberOfBlendShapes = skinnedMeshRenderer.sharedMesh.blendShapeCount;
                        AnimationCurve[] blendShapeCurves = new AnimationCurve[numberOfBlendShapes];
                        for (int j = 0; j < numberOfBlendShapes; ++j)
                            blendShapeCurves[j] = new AnimationCurve();

                        float[] weights = accessors[sampler.output].ReadFloat().ToArray();
                        float[] weightValues = new float[keyframeInput.Length];
                        float[] previouslyKeyedValues = new float[numberOfBlendShapes];
                        for (int k = 0; k < keyframeInput.Length; ++k) {
                            for (int j = 0; j < numberOfBlendShapes; ++j) {
                                int weightIndex = (k * numberOfBlendShapes) + j;
                                weightValues[k] = weights[weightIndex];

                                bool addKey = true;
                                if (importSettings.animationSettings.compressBlendShapeKeyFrames) {
                                    if (k == 0 || !Mathf.Approximately(weightValues[k], previouslyKeyedValues[j])) {
                                        if (k > 0) {
                                            weightValues[k - 1] = previouslyKeyedValues[j];
                                            blendShapeCurves[j].AddKey(CreateKeyframe(k - 1, keyframeInput, weightValues, x => x, interpolationMode));
                                        }
                                        addKey = true;
                                        previouslyKeyedValues[j] = weightValues[k];
                                    } else {
                                        addKey = false;
                                    }
                                }

                                if (addKey)
                                    blendShapeCurves[j].AddKey(CreateKeyframe(k, keyframeInput, weightValues, x => x, interpolationMode));
                            }
                        }

                        for (int j = 0; j < numberOfBlendShapes; ++j) {
                            string propertyName = "blendShape." + skinnedMeshRenderer.sharedMesh.GetBlendShapeName(j);
                            result.clip.SetCurve(relativePath, typeof(SkinnedMeshRenderer), propertyName, blendShapeCurves[j]);
                        }
                        break;
                }
            }
            return result;
        }

        public static UnityEngine.Keyframe CreateKeyframe<T>(int index, float[] timeArray, T[] valueArray, Func<T, float> getValue, InterpolationMode interpolationMode) {
            float time = timeArray[index];
            UnityEngine.Keyframe keyframe;
            if (interpolationMode == InterpolationMode.STEP) {
                keyframe = new UnityEngine.Keyframe(time, getValue(valueArray[index]), float.PositiveInfinity, float.PositiveInfinity, 1, 1);
            } else if (interpolationMode == InterpolationMode.CUBICSPLINE) {
                float inTangent = getValue(valueArray[index * 3]);
                float outTangent = getValue(valueArray[(index * 3) + 2]);
                keyframe = new UnityEngine.Keyframe(time, getValue(valueArray[(index * 3) + 1]), inTangent, outTangent, 1, 1);
            } else {
                keyframe = new UnityEngine.Keyframe(time, getValue(valueArray[index]), 0, 0, 0, 0);
            }
            return keyframe;
        }
    }

    public static class GLTFAnimationExtensions {
        public static GLTFAnimation.ImportResult[] Import(this List<GLTFAnimation> animations, GLTFAccessor.ImportResult[] accessors, GLTFNode.ImportResult[] nodes, ImportSettings importSettings) {
            if (animations == null) return null;

            GLTFAnimation.ImportResult[] results = new GLTFAnimation.ImportResult[animations.Count];
            for (int i = 0; i < results.Length; i++) {
                results[i] = animations[i].Import(accessors, nodes, importSettings);
                if (string.IsNullOrEmpty(results[i].clip.name)) results[i].clip.name = "animation" + i;
            }
            return results;
        }
    }
}