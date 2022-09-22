using UnityEngine;
using System;

namespace Simulate {
    public static class JsonHelper {
        public static T[] FromJson<T>(string json) {
            Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
            return wrapper.items;
        }

        public static string ToJson<T>(T[] array) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.items = array;
            return JsonUtility.ToJson(wrapper);
        }

        public static string ToJson<T>(T[] array, int[] shape) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.items = array;
            wrapper.shape = shape;
            return JsonUtility.ToJson(wrapper);
        }

        public static string ToJson<T>(T[] array, int[] shape, string name) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.items = array;
            wrapper.shape = shape;
            wrapper.name = name;
            return JsonUtility.ToJson(wrapper);
        }

        public static string ToJson<T>(T[] array, bool prettyPrint) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.items = array;
            return JsonUtility.ToJson(wrapper, prettyPrint);
        }

        [Serializable]
        private class Wrapper<T> {
            public T[] items;
            public int[] shape;
            public string name;
        }
    }
}