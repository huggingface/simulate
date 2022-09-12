using System.Collections.Generic;
using UnityEngine;

namespace SimEnv {
    public class StateSensor : ISensor {
        public static string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;
        private GameObject referenceEntity;
        private GameObject targetEntity;
        private List<string> properties;

        public StateSensor(Node node, SimEnv.GLTF.HFStateSensors.HFStateSensor data) {
            m_node = node;
            node.sensor = this;
            properties = data.properties;
            referenceEntity = GameObject.Find(data.reference_entity);
            if (referenceEntity != null) {
                Debug.Log("State Sensor found reference entity " + data.reference_entity);
            }
            targetEntity = GameObject.Find(data.target_entity);
            if (targetEntity != null) {
                Debug.Log("State Sensor found target entity " + data.target_entity);
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
            VALID_PROPERTIES.Add("velocity", 3);
            VALID_PROPERTIES.Add("velocity.x", 1);
            VALID_PROPERTIES.Add("velocity.y", 1);
            VALID_PROPERTIES.Add("velocity.z", 1);
            VALID_PROPERTIES.Add("rotation", 3);
            VALID_PROPERTIES.Add("rotation.x", 1);
            VALID_PROPERTIES.Add("rotation.y", 1);
            VALID_PROPERTIES.Add("rotation.z", 1);
            VALID_PROPERTIES.Add("angular_velocity", 3);
            VALID_PROPERTIES.Add("angular_velocity.x", 1);
            VALID_PROPERTIES.Add("angular_velocity.y", 1);
            VALID_PROPERTIES.Add("angular_velocity.z", 1);
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
            return mType;
        }

        public SensorBuffer GetObs() {
            SensorBuffer buffer = new SensorBuffer(GetSize(), GetShape(), GetSensorType());
            GetState(buffer);

            return buffer;
        }

        public void GetState(SensorBuffer buffer) {
            int count = 0;
            Vector3 relativePosition;
            Vector3 relativeVelocity = Vector3.zero;
            Quaternion rotation;
            Vector3 relativeAngularRotation = Vector3.zero;
            // worthwhile caching these ?
            Rigidbody referenceRigidbody = referenceEntity.GetComponent<Rigidbody>();
            Rigidbody targetEntityRigidbody = targetEntity.GetComponent<Rigidbody>();
            ArticulationBody referenceArticulationBody = referenceEntity.GetComponent<ArticulationBody>();
            ArticulationBody targetArticulationBody = targetEntity.GetComponent<ArticulationBody>();
            if (referenceEntity != null) {
                relativePosition = referenceEntity.transform.InverseTransformPoint(targetEntity.transform.position);
                rotation = Quaternion.Inverse(referenceEntity.transform.rotation) * targetEntity.transform.rotation;

                if (referenceRigidbody != null) {
                    if (targetEntityRigidbody != null) {
                        relativeVelocity = targetEntityRigidbody.velocity - referenceRigidbody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetEntityRigidbody.angularVelocity);

                    } else if (targetArticulationBody != null) {
                        relativeVelocity = targetArticulationBody.velocity - referenceRigidbody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetArticulationBody.angularVelocity);
                    }
                } else if (referenceArticulationBody != null) {
                    if (targetEntityRigidbody != null) {
                        relativeVelocity = targetEntityRigidbody.velocity - referenceArticulationBody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetEntityRigidbody.angularVelocity);

                    } else if (targetArticulationBody != null) {
                        relativeVelocity = targetArticulationBody.velocity - referenceArticulationBody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetArticulationBody.angularVelocity);
                    }
                }
                relativeVelocity = referenceEntity.transform.InverseTransformPoint(relativeVelocity);

            } else {
                relativePosition = targetEntity.transform.position;
                relativePosition = targetEntity.transform.position;
                rotation = targetEntity.transform.rotation;

                if (targetEntityRigidbody != null) {
                    relativeVelocity = targetEntityRigidbody.velocity;
                } else if (targetArticulationBody != null) {
                    relativeVelocity = targetArticulationBody.velocity;
                }
            }

            foreach (var property in properties) {
                switch (property) {
                    case "position":
                        buffer.floatBuffer[count] = relativePosition.x;
                        buffer.floatBuffer[count + 1] = relativePosition.y;
                        buffer.floatBuffer[count + 2] = relativePosition.z;
                        count += 3;
                        break;
                    case "position.x":
                        buffer.floatBuffer[count] = relativePosition.x;
                        count += 1;
                        break;
                    case "position.y":
                        buffer.floatBuffer[count] = relativePosition.y;
                        count += 1;
                        break;
                    case "position.z":
                        buffer.floatBuffer[count] = relativePosition.y;
                        count += 1;
                        break;
                    case "velocity":
                        buffer.floatBuffer[count] = relativeVelocity.x;
                        buffer.floatBuffer[count + 1] = relativeVelocity.y;
                        buffer.floatBuffer[count + 2] = relativeVelocity.z;
                        count += 3;
                        break;
                    case "velocity.x":
                        buffer.floatBuffer[count] = relativeVelocity.x;
                        count += 1;
                        break;
                    case "velocity.y":
                        buffer.floatBuffer[count] = relativeVelocity.y;
                        count += 1;
                        break;
                    case "velocity.z":
                        buffer.floatBuffer[count] = relativeVelocity.y;
                        count += 1;
                        break;
                    case "rotation":
                        buffer.floatBuffer[count] = rotation.x;
                        buffer.floatBuffer[count + 1] = rotation.y;
                        buffer.floatBuffer[count + 2] = rotation.z;
                        count += 3;
                        break;
                    case "rotation.x":
                        buffer.floatBuffer[count] = rotation.x;
                        count += 1;
                        break;
                    case "rotation.y":
                        buffer.floatBuffer[count] = rotation.y;
                        count += 1;
                        break;
                    case "rotation.z":
                        buffer.floatBuffer[count] = rotation.z;
                        count += 1;
                        break;
                    case "angular_velocity":
                        buffer.floatBuffer[count] = relativeAngularRotation.x;
                        buffer.floatBuffer[count + 1] = relativeAngularRotation.y;
                        buffer.floatBuffer[count + 2] = relativeAngularRotation.z;
                        count += 3;
                        break;
                    case "angular_velocity.x":
                        buffer.floatBuffer[count] = relativeAngularRotation.x;
                        count += 1;
                        break;
                    case "angular_velocity.y":
                        buffer.floatBuffer[count] = relativeAngularRotation.y;
                        count += 1;
                        break;
                    case "angular_velocity.z":
                        buffer.floatBuffer[count] = relativeAngularRotation.z;
                        count += 1;
                        break;
                    case "distance":
                        buffer.floatBuffer[count] = relativePosition.magnitude;
                        count += 1;
                        break;
                    default:
                        Debug.Assert(false, "incompatable property provided");
                        break;
                }
            }
        }

        public void Enable() { }
        public void Disable() { }
    }
}