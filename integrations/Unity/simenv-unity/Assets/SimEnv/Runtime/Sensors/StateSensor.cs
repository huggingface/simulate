using System.Collections.Generic;
using UnityEngine;

namespace SimEnv {
    public class StateSensor : ISensor {
        public string mName = "StateSensor";
        public static string mType = "float";
        public Node node => m_node;
        Node m_node;
        private GameObject referenceEntity;
        private GameObject targetEntity;
        private List<string> properties;

        public StateSensor(Node node, SimEnv.GLTF.HFStateSensors.HFStateSensor data) {
            m_node = node;
            node.sensor = this;
            mName = data.sensor_name;
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

        // public string GetBufferType() {
        //     return mType;
        // }

        public Buffer GetObs(Buffer buffer, int mapIndex, int actorIndex) {
            Buffer oldBuffer = new Buffer(GetSize(), GetShape(), GetSensorBufferType());
            GetState(oldBuffer, buffer, mapIndex, actorIndex);

            return oldBuffer;
        }

        public void GetState(Buffer oldBuffer, Buffer buffer, int mapIndex, int actorIndex) {
            int count = 0;
            int startingIndex = mapIndex * actorIndex * GetSize();
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
                        oldBuffer.floatBuffer[count] = relativePosition.x;
                        oldBuffer.floatBuffer[count + 1] = relativePosition.y;
                        oldBuffer.floatBuffer[count + 2] = relativePosition.z;
                        buffer.floatBuffer[count + startingIndex] = relativePosition.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativePosition.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativePosition.z;
                        count += 3;
                        break;
                    case "position.x":
                        oldBuffer.floatBuffer[count] = relativePosition.x;
                        buffer.floatBuffer[count + startingIndex] = relativePosition.x;
                        count += 1;
                        break;
                    case "position.y":
                        oldBuffer.floatBuffer[count] = relativePosition.y;
                        buffer.floatBuffer[count + startingIndex] = relativePosition.y;
                        count += 1;
                        break;
                    case "position.z":
                        oldBuffer.floatBuffer[count] = relativePosition.z;
                        buffer.floatBuffer[count + startingIndex] = relativePosition.z;
                        count += 1;
                        break;
                    case "velocity":
                        oldBuffer.floatBuffer[count] = relativeVelocity.x;
                        oldBuffer.floatBuffer[count + 1] = relativeVelocity.y;
                        oldBuffer.floatBuffer[count + 2] = relativeVelocity.z;
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativeVelocity.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativeVelocity.z;
                        count += 3;
                        break;
                    case "velocity.x":
                        oldBuffer.floatBuffer[count] = relativeVelocity.x;
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.x;
                        count += 1;
                        break;
                    case "velocity.y":
                        oldBuffer.floatBuffer[count] = relativeVelocity.y;
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.y;
                        count += 1;
                        break;
                    case "velocity.z":
                        oldBuffer.floatBuffer[count] = relativeVelocity.z;
                        buffer.floatBuffer[count + startingIndex] = relativeVelocity.z;
                        count += 1;
                        break;
                    case "rotation":
                        oldBuffer.floatBuffer[count] = rotation.x;
                        oldBuffer.floatBuffer[count + 1] = rotation.y;
                        oldBuffer.floatBuffer[count + 2] = rotation.z;

                        buffer.floatBuffer[count + startingIndex] = rotation.x;
                        buffer.floatBuffer[count + startingIndex + 1] = rotation.y;
                        buffer.floatBuffer[count + startingIndex + 2] = rotation.z;
                        count += 3;
                        break;
                    case "rotation.x":
                        oldBuffer.floatBuffer[count] = rotation.x;
                        buffer.floatBuffer[count + startingIndex] = rotation.x;
                        count += 1;
                        break;
                    case "rotation.y":
                        oldBuffer.floatBuffer[count] = rotation.y;
                        buffer.floatBuffer[count + startingIndex] = rotation.y;
                        count += 1;
                        break;
                    case "rotation.z":
                        oldBuffer.floatBuffer[count] = rotation.z;
                        buffer.floatBuffer[count + startingIndex] = rotation.z;
                        count += 1;
                        break;
                    case "angular_velocity":
                        oldBuffer.floatBuffer[count] = relativeAngularRotation.x;
                        oldBuffer.floatBuffer[count + 1] = relativeAngularRotation.y;
                        oldBuffer.floatBuffer[count + 2] = relativeAngularRotation.z;
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.x;
                        buffer.floatBuffer[count + startingIndex + 1] = relativeAngularRotation.y;
                        buffer.floatBuffer[count + startingIndex + 2] = relativeAngularRotation.z;

                        count += 3;
                        break;
                    case "angular_velocity.x":
                        oldBuffer.floatBuffer[count] = relativeAngularRotation.x;
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.x;
                        count += 1;
                        break;
                    case "angular_velocity.y":
                        oldBuffer.floatBuffer[count] = relativeAngularRotation.y;
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.y;
                        count += 1;
                        break;
                    case "angular_velocity.z":
                        oldBuffer.floatBuffer[count] = relativeAngularRotation.z;
                        buffer.floatBuffer[count + startingIndex] = relativeAngularRotation.z;
                        count += 1;
                        break;
                    case "distance":
                        oldBuffer.floatBuffer[count] = relativePosition.magnitude;
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