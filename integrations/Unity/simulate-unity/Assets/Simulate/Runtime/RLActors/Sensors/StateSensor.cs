using System.Collections.Generic;
using UnityEngine;

namespace Simulate {
    public class StateSensor : ISensor {
        public string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;

        Node m_node;
        GameObject referenceEntity;
        GameObject targetEntity;
        Rigidbody referenceRigidbody;
        Rigidbody targetRigidbody;
        ArticulationBody referenceArticulationBody;
        ArticulationBody targetArticulationBody;
        List<string> properties;

        public StateSensor(Node node, Simulate.GLTF.HFStateSensors.HFStateSensor data) {
            m_node = node;
            mName = data.sensor_tag;
            properties = data.properties;
            referenceEntity = GameObject.Find(data.reference_entity);
            targetEntity = GameObject.Find(data.target_entity);
            if (targetEntity != null) {
                targetRigidbody = targetEntity.GetComponent<Rigidbody>();
                targetArticulationBody = targetEntity.GetComponent<ArticulationBody>();
            } else {
                Debug.LogWarning("State sensor target entity not found: " + data.target_entity);
            }
            if (referenceEntity != null) {
                referenceRigidbody = referenceEntity.GetComponent<Rigidbody>();
                referenceArticulationBody = referenceEntity.GetComponent<ArticulationBody>();
            }
        }

        public string GetName() {
            return mName;
        }

        public string GetSensorBufferType() {
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

        public void AddObsToBuffer(Buffer buffer, int bufferIndex) {
            GetState(buffer, bufferIndex);
        }

        public void GetState(Buffer buffer, int bufferIndex) {
            int count = 0;
            int startingIndex = bufferIndex * GetSize();
            Vector3 relativePosition;
            Vector3 relativeVelocity = Vector3.zero;
            Quaternion rotation;
            Vector3 relativeAngularRotation = Vector3.zero;
            if (referenceEntity != null) {
                relativePosition = referenceEntity.transform.InverseTransformPoint(targetEntity.transform.position);
                rotation = Quaternion.Inverse(referenceEntity.transform.rotation) * targetEntity.transform.rotation;

                if (referenceRigidbody != null) {
                    if (targetRigidbody != null) {
                        relativeVelocity = targetRigidbody.velocity - referenceRigidbody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetRigidbody.angularVelocity);

                    } else if (targetArticulationBody != null) {
                        relativeVelocity = targetArticulationBody.velocity - referenceRigidbody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetArticulationBody.angularVelocity);
                    }
                } else if (referenceArticulationBody != null) {
                    if (targetRigidbody != null) {
                        relativeVelocity = targetRigidbody.velocity - referenceArticulationBody.velocity;
                        relativeAngularRotation = referenceEntity.transform.InverseTransformDirection(targetRigidbody.angularVelocity);

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

                if (targetRigidbody != null) {
                    relativeVelocity = targetRigidbody.velocity;
                } else if (targetArticulationBody != null) {
                    relativeVelocity = targetArticulationBody.velocity;
                }
            }

            foreach (var property in properties) {
                switch (property) {
                    case "position":
                        buffer.floatBuffer[count + startingIndex] = relativePosition.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativePosition.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativePosition.z;
                        count += 3;
                        break;
                    case "position.x":
                        buffer.floatBuffer[count + startingIndex] = relativePosition.x;
                        count += 1;
                        break;
                    case "position.y":
                        buffer.floatBuffer[count + startingIndex] = relativePosition.y;
                        count += 1;
                        break;
                    case "position.z":
                        buffer.floatBuffer[count + startingIndex] = relativePosition.z;
                        count += 1;
                        break;
                    case "velocity":
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativeVelocity.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativeVelocity.z;
                        count += 3;
                        break;
                    case "velocity.x":
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.x;
                        count += 1;
                        break;
                    case "velocity.y":
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.y;
                        count += 1;
                        break;
                    case "velocity.z":
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.z;
                        count += 1;
                        break;
                    case "rotation":
                        buffer.floatBuffer[count + startingIndex] = rotation.x;
                        buffer.floatBuffer[count + startingIndex + 1] = rotation.y;
                        buffer.floatBuffer[count + startingIndex + 2] = rotation.z;
                        count += 3;
                        break;
                    case "rotation.x":
                        buffer.floatBuffer[count + startingIndex] = rotation.x;
                        count += 1;
                        break;
                    case "rotation.y":
                        buffer.floatBuffer[count + startingIndex] = rotation.y;
                        count += 1;
                        break;
                    case "rotation.z":
                        buffer.floatBuffer[count + startingIndex] = rotation.z;
                        count += 1;
                        break;
                    case "angular_velocity":
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativeAngularRotation.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativeAngularRotation.z;

                        count += 3;
                        break;
                    case "angular_velocity.x":
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.x;
                        count += 1;
                        break;
                    case "angular_velocity.y":
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.y;
                        count += 1;
                        break;
                    case "angular_velocity.z":
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.z;
                        count += 1;
                        break;
                    case "distance":
                        buffer.floatBuffer[count + startingIndex] = relativePosition.magnitude;
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