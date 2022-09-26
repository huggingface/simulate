// adapted from https://github.com/Siccity/GLTFUtility/tree/master/Scripts/Converters/ColorConverter.cs
using UnityEngine;
using Newtonsoft.Json;
using System;

public class ColorRGBConverter : JsonConverter {
    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
        Color color = (Color)value;
        writer.WriteStartArray();
        writer.WriteValue(color.r);
        writer.WriteValue(color.g);
        writer.WriteValue(color.b);
        writer.WriteEndArray();
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
        float[] floatArray = serializer.Deserialize<float[]>(reader);
        return new Color(floatArray[0], floatArray[1], floatArray[2]);
    }

    public override bool CanConvert(Type objectType) {
        return objectType == typeof(Color);
    }
}

public class ColorRGBAConverter : JsonConverter {
    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
        Color color = (Color)value;
        writer.WriteStartArray();
        writer.WriteValue(color.r);
        writer.WriteValue(color.g);
        writer.WriteValue(color.b);
        writer.WriteValue(color.a);
        writer.WriteEndArray();
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
        float[] floatArray = serializer.Deserialize<float[]>(reader);
        return new Color(floatArray[0], floatArray[1], floatArray[2], floatArray[3]);
    }

    public override bool CanConvert(Type objectType) {
        return objectType == typeof(Color);
    }
}
