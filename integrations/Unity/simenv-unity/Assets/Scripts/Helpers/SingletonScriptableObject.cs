using UnityEngine;

public class SingletonScriptableObject<T> : ScriptableObject where T : SingletonScriptableObject<T>
{
    static T instance;
    public static T Instance {
        get {
            if(instance == null) {
                T[] assets = Resources.LoadAll<T>("");
                if(assets == null || assets.Length < 1)
                    throw new System.Exception("Couldn't find singleton scriptable object instance of type " + typeof(T));
                else if(assets.Length > 1)
                    throw new System.Exception("Found multiple singleton scriptable objects of type " + typeof(T));
                instance = assets[0];
            }
            return instance;
        }
    }
}
