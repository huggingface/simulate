using UnityEngine;
// adapted from https://github.com/Siccity/GLTFUtility/tree/master/Scripts/Converters/EnumConverter.cs
using Newtonsoft.Json;
using System;

public class EnumConverter : JsonConverter {
    public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
        writer.WriteValue(value.ToString());
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
        string value = serializer.Deserialize<string>(reader);
        if (Enum.IsDefined(objectType, value))
            return Enum.Parse(objectType, value);
        else
            return existingValue;
    }

    public override bool CanConvert(Type objectType) {
        return typeof(Enum).IsAssignableFrom(objectType);
    }
}
