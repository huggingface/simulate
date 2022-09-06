using Newtonsoft.Json;
using UnityEngine;

namespace SimEnv {
    public class SensorBuffer {
        public float[] floatBuffer;
        public uint[] uintBuffer;
        public string type;
        public int[] shape;

        public SensorBuffer(int size, int[] shape, string type) {
            this.type = type;
            this.shape = shape;
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
                Debug.Log("trying to create SensorBuffer with unknown type " + type);
                return "";
            }
        }
    }

    public interface ISensor {
        string GetName();
        string GetSensorType();
        int GetSize();
        int[] GetShape();
        void Enable();
        void Disable();
        string GetBufferType();
        SensorBuffer GetObs();
    }
}