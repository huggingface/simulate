// adapted from https://github.com/Siccity/GLTFUtility/blob/3d5d97d7e174bde3c5e58b6f02301de36f7f6eb7/Scripts/Extensions.cs
using System;
using System.Collections;
using UnityEngine;

namespace SimEnv.GLTF {
    public static class Extensions {
        public class CoroutineRunner : MonoBehaviour { }
        private static CoroutineRunner coroutineRunner;
        public static Coroutine RunCoroutine(this IEnumerator ienum) {
            if(coroutineRunner == null) {
                coroutineRunner = new GameObject("[CoroutineRunner]").AddComponent<CoroutineRunner>();
                coroutineRunner.hideFlags = HideFlags.DontSaveInEditor | HideFlags.HideInHierarchy | HideFlags.HideInInspector | HideFlags.NotEditable | HideFlags.DontSaveInBuild;
                coroutineRunner.gameObject.hideFlags = HideFlags.DontSaveInEditor | HideFlags.HideInHierarchy | HideFlags.HideInInspector | HideFlags.NotEditable | HideFlags.DontSaveInBuild;
            }
            return coroutineRunner.StartCoroutine(ienum);
        }

        public static T[] SubArray<T>(this T[] data, int index, int length) {
            T[] result = new T[length];
            Array.Copy(data, index, result, 0, length);
            return result;
        }

        public static void UnpackMatrix(this Matrix4x4 matrix, ref Vector3 position, ref Quaternion rotation, ref Vector3 scale) {
            position = matrix.GetColumn(3);
            position.x = -position.x;
            rotation = matrix.rotation;
            rotation = new Quaternion(rotation.x, -rotation.y, -rotation.z, rotation.w);
            scale = matrix.lossyScale;
        }
    }
}