using System;
using UnityEngine;

public abstract class PolymorphicObject
{
    public string assemblyQualifiedName;

    public static T FromJson<T>(string json) where T : PolymorphicObject {
        Type type = Type.GetType(JsonUtility.FromJson<T>(json).assemblyQualifiedName);
        return (T)JsonUtility.FromJson(json, type);
    }

    public PolymorphicObject() {
        Type type = GetType();
        assemblyQualifiedName = type.AssemblyQualifiedName;
    }
}