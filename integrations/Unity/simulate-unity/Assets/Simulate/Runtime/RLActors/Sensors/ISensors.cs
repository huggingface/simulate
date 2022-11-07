using Newtonsoft.Json;
using UnityEngine;

namespace Simulate {
    public class Buffer {
        public float[] floatBuffer;
        public uint[] uintBuffer;
        public string type;
        public int[] shape;

        public int size;

        public Buffer(int size, int[] shape, string type) {
            this.type = type;
            this.shape = shape;
            this.size = size;
            if (type == "float") {
                floatBuffer = new float[size];
            } else if (type == "uint8") {
                uintBuffer = new uint[size];
            } else {
                Debug.Log("trying to create SensorBuffer with unknown type " + type);
            }
        }

        public string ToJson(int[] shape, string name) {
            if (type == "float") {
                return JsonHelper.ToJson(floatBuffer, shape, name);
            } else if (type == "uint8") {
                return JsonHelper.ToJson(uintBuffer, shape, name);
            } else {
                Debug.Log("trying to parse SensorBuffer with unknown type " + type);
                return "";
            }
        }
    }

    public interface ISensor {
        string GetName();
        string GetSensorBufferType();
        int GetSize();
        int[] GetShape();
        void Enable();
        void Disable();
        void AddObsToBuffer(Buffer buffer, int bufferIndex);
    }
}