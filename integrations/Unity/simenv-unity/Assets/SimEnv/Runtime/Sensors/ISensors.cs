using UnityEngine;
using UnityEngine.Events;
using System.Collections;

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

        public string GetName();
        public string GetSensorType();
        public int GetSize();
        public int[] GetShape();
        public void Enable();
        public void Disable();
        public string GetBufferType();
        public IEnumerator GetObs(SensorBuffer buffer, int index);
        public SensorBuffer GetObs();
    }
}