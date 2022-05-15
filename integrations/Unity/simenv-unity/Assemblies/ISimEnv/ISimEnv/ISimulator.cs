using UnityEngine;
using System.Collections.Generic;

namespace ISimEnv {
    /// <summary>
    /// Exposes simulator functionality to modding API
    /// </summary>
    public class ISimulator {
        static Dictionary<string, ISimObject> _objects;
        static Dictionary<string, ISimObject> objects {
            get {
                if(_objects == null)
                    _objects = new Dictionary<string, ISimObject>();
                return _objects;
            }
        }

        public static void Add(GameObject gameObject) {

        }

        public static void Register(ISimObject simObject) {
            if(objects.ContainsKey(simObject.Name)) {
                Debug.LogError("Environment already contains object with name: " + simObject.Name);
                return;
            }
            objects.Add(simObject.Name, simObject);
            simObject.OnDeinitialize += Unregister;
        }

        public static void Unregister(ISimObject simObject) {
            simObject.OnDeinitialize -= Unregister;
            objects.Remove(simObject.Name);
        }

        public static ISimObject GetObject(string identifier) {
            if(!objects.ContainsKey(identifier)) {
                Debug.LogError("Couldn't find object with identifier: " + identifier);
                return null;
            }
            return objects[identifier];
        }

        public static bool TryGetObject(string identifier, out ISimObject simObject) {
            simObject = null;
            if(objects.ContainsKey(identifier)) {
                simObject = objects[identifier];
                return true;
            }
            return false;
        }
    }
}
