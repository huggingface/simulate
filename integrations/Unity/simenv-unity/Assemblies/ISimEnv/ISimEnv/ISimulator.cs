using UnityEngine;
using System.Collections.Generic;

namespace ISimEnv {
    /// <summary>
    /// References all SimObjects
    /// </summary>
    public class ISimulator {
        static ISimulator _instance;
        public static ISimulator Instance {
            get {
                if (_instance == null)
                    _instance = new ISimulator();
                return _instance;
            }
        }

        static Dictionary<string, ISimObject> _objects;
        static Dictionary<string, ISimObject> objects {
            get {
                if(_objects == null)
                    _objects = new Dictionary<string, ISimObject>();
                return _objects;
            }
        }

        public static void Register(ISimObject simObject) {
            if(objects.ContainsKey(simObject.Name)) {
                Debug.LogWarning("Environment already contains object with name: " + simObject.Name);
                return;
            }
            objects.Add(simObject.Name, simObject);
        }

        public static void Unregister(ISimObject simObject) {
            if(!objects.ContainsKey(simObject.Name)) {
                Debug.LogWarning(string.Format("Object with name {0} not found", simObject.Name));
                return;
            }
            objects.Remove(simObject.Name);
        }

        public static ISimObject GetObject(string identifier) {
            if(!objects.ContainsKey(identifier)) {
                Debug.LogWarning("Couldn't find object with identifier: " + identifier);
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
