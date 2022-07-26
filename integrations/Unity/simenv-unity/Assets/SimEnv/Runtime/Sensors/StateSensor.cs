using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace SimEnv {
    public class StateSensor : ISensor {
        public static string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;
        private GameObject reference_entity;
        private GameObject target_entity;
        private List<string> properties;

        public StateSensor(Node node, SimEnv.GLTF.HFStateSensors.HFStateSensor data) {
            m_node = node;
            node.sensor = this;
            properties = data.properties;

            Debug.Log("State Sensor finding reference entity " + data.reference_entity_name);
            reference_entity = GameObject.Find(data.reference_entity_name);
            if (reference_entity != null) {
                Debug.Log("State Sensor found reference entity " + data.reference_entity_name);
            }
            Debug.Log("State Sensor finding target entity " + data.target_entity_name);
            target_entity = GameObject.Find(data.target_entity_name);
            if (target_entity != null) {
                Debug.Log("State Sensor found target entity " + data.target_entity_name);
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
            Dictionary<string, int> VALID_PROPERTIES = new Dictionary<string, int>();
            VALID_PROPERTIES.Add("position", 3);
            VALID_PROPERTIES.Add("position.x", 1);
            VALID_PROPERTIES.Add("position.y", 1);
            VALID_PROPERTIES.Add("position.z", 1);
            VALID_PROPERTIES.Add("rotation", 3);
            VALID_PROPERTIES.Add("rotation.x", 1);
            VALID_PROPERTIES.Add("rotation.y", 1);
            VALID_PROPERTIES.Add("rotation.z", 1);
            VALID_PROPERTIES.Add("distance", 1);

            int nFeatures = 0;
            foreach (var property in properties) {
                nFeatures += VALID_PROPERTIES[property];
            }

            return nFeatures;
        }

        public int[] GetShape() {
            int[] shape = { GetSize() };
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
            // TODO: these should be transformed into the frame of reference of the reference entity
            Vector3 relative_position = target_entity.transform.position - reference_entity.transform.position;
            Vector3 rotation = target_entity.transform.eulerAngles;

            foreach (var property in properties) {
                switch (property) {
                    case "position":
                        buffer.floatBuffer[index + subIndex] = relative_position.x;
                        buffer.floatBuffer[index + subIndex + 1] = relative_position.y;
                        buffer.floatBuffer[index + subIndex + 2] = relative_position.z;
                        subIndex += 3;
                        break;
                    case "position.x":
                        buffer.floatBuffer[index + subIndex] = relative_position.x;
                        subIndex += 1;
                        break;
                    case "position.y":
                        buffer.floatBuffer[index + subIndex] = relative_position.y;
                        subIndex += 1;
                        break;
                    case "position.z":
                        buffer.floatBuffer[index + subIndex] = relative_position.y;
                        subIndex += 1;
                        break;
                    case "rotation":
                        buffer.floatBuffer[index + subIndex] = rotation.x;
                        buffer.floatBuffer[index + subIndex + 1] = rotation.y;
                        buffer.floatBuffer[index + subIndex + 2] = rotation.z;
                        subIndex += 3;
                        break;
                    case "rotation.x":
                        buffer.floatBuffer[index + subIndex] = rotation.x;
                        subIndex += 1;
                        break;
                    case "rotation.y":
                        buffer.floatBuffer[index + subIndex] = rotation.y;
                        subIndex += 1;
                        break;
                    case "rotation.z":
                        buffer.floatBuffer[index + subIndex] = rotation.y;
                        subIndex += 1;
                        break;
                    case "distance":
                        buffer.floatBuffer[index + subIndex] = relative_position.magnitude;
                        subIndex += 1;
                        break;
                    default:
                        Debug.Assert(false, "incompatable property provided");
                        break;
                }
            }
        }
    }
}