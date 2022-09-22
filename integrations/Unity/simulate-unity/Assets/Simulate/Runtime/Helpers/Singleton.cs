using UnityEngine;

namespace Simulate {
    public abstract class Singleton<T> : ScriptableObject where T : Singleton<T> {
        static T _instance;
        public static T instance {
            get {
                if (_instance == null) {
                    T[] assets = Resources.LoadAll<T>("Singletons");
                    if (assets == null || assets.Length < 1)
                        throw new System.Exception("Couldn't find Singleton of type " + typeof(T));
                    else if (assets.Length > 1)
                        throw new System.Exception("Found multiple Singletons of type " + typeof(T));
                    _instance = assets[0];
                }
                return _instance;
            }
        }
    }
}