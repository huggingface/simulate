using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace Simulate {
    public class EventData {
        [JsonIgnore] public Dictionary<string, object> inputKwargs;
        [JsonIgnore] public Dictionary<string, object> outputKwargs;
        public Dictionary<string, Node.Data> nodes;
        public Dictionary<string, uint[,,]> frames;

        public EventData() {
            nodes = new Dictionary<string, Node.Data>();
            frames = new Dictionary<string, uint[,,]>();
            inputKwargs = new Dictionary<string, object>();
            outputKwargs = new Dictionary<string, object>();
        }
    }

    public class EventDataConverter : JsonConverter {
        public override bool CanRead => false;

        public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer) {
            throw new NotImplementedException();
        }

        public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer) {
            EventData eventData = value as EventData;
            JObject jo = JObject.FromObject(eventData);
            foreach (string key in eventData.outputKwargs.Keys) {
                jo.Add(key, JObject.FromObject(eventData.outputKwargs[key]));

            }
            jo.WriteTo(writer);
        }

        public override bool CanConvert(Type objectType) {
            return objectType == typeof(EventData);
        }
    }
}