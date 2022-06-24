// adapted from https://github.com/Siccity/GLTFUtility/blob/3d5d97d7e174bde3c5e58b6f02301de36f7f6eb7/Scripts/Extensions.cs
using System;
using System.Collections;
using UnityEngine;

namespace SimEnv {
    public static class Extensions {
        public static Coroutine RunCoroutine(this IEnumerator item) {
            if(Simulator.instance == null) {
                Debug.LogWarning("No simulator found");
                return null;
            }
            return Simulator.instance.StartCoroutine(item);
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