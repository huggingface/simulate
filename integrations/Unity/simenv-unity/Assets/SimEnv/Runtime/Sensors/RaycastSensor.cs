using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace SimEnv {
    public class RaycastSensor : ISensor {
        public static string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;
        private GameObject referenceEntity;
        private GameObject targetEntity;
        private List<string> properties;

        public RaycastSensor(Node node, SimEnv.GLTF.HFRaycastSensors.HFRaycastSensor data) {
            m_node = node;
            node.sensor = this;
            // calculate ray angles etc
            Debug.Log("instantiating raycast sensor");

        }
        public string GetName() {
            return mName;
        }
        public string GetSensorType() {
            return mType;
        }
        public int GetSize() {
            return 1;
        }

        public int[] GetShape() {
            int[] shape = { GetSize() };
            return shape;
        }

        public string GetBufferType() {
            return mType;
        }
        public SensorBuffer GetObs() {
            SensorBuffer buffer = new SensorBuffer(GetSize(), GetShape(), GetSensorType());
            GetState(buffer);

            return buffer;
        }
        public void GetState(SensorBuffer buffer) {

        }
        public void Enable() {

        }

        public void Disable() {

        }
    }
}