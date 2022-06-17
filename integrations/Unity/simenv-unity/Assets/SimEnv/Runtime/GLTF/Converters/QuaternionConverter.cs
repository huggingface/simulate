using UnityEngine;
// adapted from https://github.com/Siccity/GLTFUtility/tree/master/Scripts/Converters/QuaternionConverter.cs
using Newtonsoft.Json;
using System;

public class QuaternionConverter : JsonConverter {
    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
        Quaternion rot = (Quaternion)value;
        writer.WriteStartArray();
        writer.WriteValue(rot.x);
        writer.WriteValue(-rot.y);
        writer.WriteValue(-rot.z);
        writer.WriteValue(rot.w);
        writer.WriteEndArray();
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
        float[] floatArray = serializer.Deserialize<float[]>(reader);
        return new Quaternion(floatArray[0], -floatArray[1], -floatArray[2], floatArray[3]);
    }

    public override bool CanConvert(Type objectType) {
        return objectType == typeof(Quaternion);
    }
}
