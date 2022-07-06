// adapted from https://github.com/Siccity/GLTFUtility/tree/master/Scripts/Converters/Vector2Converter.cs
using UnityEngine;
using Newtonsoft.Json;
using System;

public class Vector2Converter : JsonConverter {
    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
        Vector2 pos = (Vector2)value;
        writer.WriteStartArray();
        writer.WriteValue(pos.x);
        writer.WriteValue(pos.y);
        writer.WriteEndArray();
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
        float[] floatArray = null;
        try {
            floatArray = serializer.Deserialize<float[]>(reader);
        } catch (System.Exception) {
            floatArray = new float[] { serializer.Deserialize<float>(reader) };
        }

        switch (floatArray.Length) {
            case 1:
                return new Vector2(floatArray[0], floatArray[0]);
            case 2:
                return new Vector2(floatArray[0], floatArray[1]);
            case 3:
                return new Vector2(floatArray[0], floatArray[1]);
            default:
                return Vector2.one;
        }
    }

    public override bool CanConvert(Type objectType) {
        return objectType == typeof(Vector2);
    }
}
