using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace SimEnv.GLTF {
    public class HFCameraSensors {
        public List<HFCameraSensor> camera_sensors;

        public HFCameraSensors() {
            camera_sensors = new List<HFCameraSensor>();
        }
        public class HFCameraSensor {
            public Orthographic orthographic;
            public Perspective perspective;
            [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public CameraType type;
            public string name;
            public int width = 512;
            public int height = 512;

            public class Orthographic {
                [JsonProperty(Required = Required.Always)] public float xmag;
                [JsonProperty(Required = Required.Always)] public float ymag;
                [JsonProperty(Required = Required.Always)] public float zfar;
                [JsonProperty(Required = Required.Always)] public float znear;
            }

            public class Perspective {
                public float? aspectRatio;
                [JsonProperty(Required = Required.Always)] public float yfov;
                public float? zfar;
                [JsonProperty(Required = Required.Always)] public float znear;
            }
        }

    }

}