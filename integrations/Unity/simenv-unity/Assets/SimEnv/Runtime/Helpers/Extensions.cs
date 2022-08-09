// adapted from https://github.com/Siccity/GLTFUtility/blob/3d5d97d7e174bde3c5e58b6f02301de36f7f6eb7/Scripts/Extensions.cs
using System;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace SimEnv {
    public static class Extensions {
        public static Coroutine RunCoroutine(this IEnumerator item) {
            if (Simulator.instance == null) {
                Debug.LogWarning("No simulator found");
                return null;
            }
            return Simulator.instance.StartCoroutine(item);
        }

        public static T Parse<T>(this Dictionary<string, object> kwargs, string key, bool silent = false) {
            if (!kwargs.TryGetValue(key, out object value)) {
                if(!silent)
                    Debug.LogWarning("Key not found in kwargs");
                return default(T);
            }
            try {
                if (typeof(T).IsPrimitive)
                    return (T)Convert.ChangeType(value, typeof(T));
                JObject jObject = JObject.FromObject(value);
                return jObject.ToObject<T>();
            } catch(Exception e) {
                Debug.LogWarning($"Failed to parse object with key {key} to type {typeof(T)}: {e}");
                return default(T);
            }
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

        public static Texture2D Decompress(this Texture2D source) {
            RenderTexture renderTexture = RenderTexture.GetTemporary(
                source.width,
                source.height,
                24,
                RenderTextureFormat.Default
            );
            Graphics.Blit(source, renderTexture);
            RenderTexture active = RenderTexture.active;
            RenderTexture.active = renderTexture;
            Texture2D tex = new Texture2D(source.width, source.height);
            tex.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
            tex.Apply();
            RenderTexture.active = active;
            RenderTexture.ReleaseTemporary(renderTexture);
            return tex;
        }
    }
}