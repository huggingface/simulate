using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace SimEnv {
    public class StateSensor : ISensor {
        public static string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;
        private string entity_name;

        private GameObject entity;
        private List<string> properties;

        public StateSensor(Node node, SimEnv.GLTF.HFStateSensors.HFStateSensor data) {
            m_node = node;
            node.sensor = this;
            entity_name = data.entity_name;
            properties = data.properties;

            Debug.Log("State Sensor finding entity " + entity_name);
            entity = GameObject.Find(entity_name);
            if (entity != null) {
                Debug.Log("State Sensor found entity " + entity_name);
            }

            foreach (var property in properties) {
                Debug.Log("property: " + property);
            }


        }
        public string GetName() {
            return mName;
        }
        public string GetSensorType() {
            return mType;
        }
        public int GetSize() {
            return properties.Count * 3; // debugging 
        }

        public int[] GetShape() {
            int[] shape = { properties.Count * 3 };
            return shape;
        }

        public string GetBufferType() {
            return "float";
        }


        public IEnumerator GetObs(SensorBuffer buffer, int index) {
            // TODO: I do not think this is require for physical properties ?
            yield return new WaitForEndOfFrame(); // Wait for Unity to render 
            GetState(buffer, index);
        }

        public void GetState(SensorBuffer buffer, int index) {
            int subIndex = 0;

            if (properties.Contains("position")) {
                Vector3 position = entity.transform.position;
                buffer.floatBuffer[index + subIndex] = position.x;
                buffer.floatBuffer[index + subIndex + 1] = position.y;
                buffer.floatBuffer[index + subIndex + 2] = position.z;
                subIndex += 3;
            }
            if (properties.Contains("rotation")) {
                Vector3 rotation = entity.transform.eulerAngles;
                buffer.floatBuffer[index + subIndex] = rotation.x;
                buffer.floatBuffer[index + subIndex + 1] = rotation.y;
                buffer.floatBuffer[index + subIndex + 2] = rotation.z;
                subIndex += 3;
            }

        }
    }
}