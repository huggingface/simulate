using System.Collections.Generic;
using UnityEngine;
using System;
using Simulate.GLTF;

namespace Simulate.RlAgents {
    public static class Actions {
        public static void ExecuteAction(this Actor actor, Dictionary<string, List<float>> actions) {
            foreach (KeyValuePair<string, List<float>> action in actions) {
                if (actor.actuatorNodes.TryGetValue(action.Key, out Node node)) {
                    var actionIndex = 0;
                    foreach (float subAction in action.Value) {
                        (float value, HFActuators.ActionMapping mapping) = node.actuator.GetMapping(actionIndex, subAction);
                        Debug.Log($"Execute sub action {actionIndex}: {value}, {mapping.action}");
                        actionIndex++;
                        switch (mapping.action) {
                            case "add_force":
                                node.AddForce(value, mapping);
                                break;
                            case "add_torque":
                                node.AddTorque(value, mapping);
                                break;
                            case "add_force_at_position":
                                node.AddForceAtPosition(value, mapping);
                                break;
                            case "change_position":
                                node.ChangePosition(value, mapping);
                                break;
                            case "change_rotation":
                                node.ChangeRotation(value, mapping);
                                break;
                            case "set_position":
                                node.SetPosition(value, mapping);
                                break;
                            case "set_rotation":
                                node.SetRotation(value, mapping);
                                break;
                            case "do_nothing":
                                break;
                        }
                    }
                }
            }
        }

        public static void AddForce(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Force' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;
            Vector3 force = mapping.axis.Value.normalized * magnitude;

            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;

            // Debug.Log("AddForce, force: " + force + " relative:"
            //     + mapping.useLocalCoordinates + " isImpulse:" + mapping.isImpulse);

            if (node.rigidbody != null) {
                if (mapping.useLocalCoordinates) {
                    node.rigidbody.AddRelativeForce(force, forceMode);
                } else {
                    node.rigidbody.AddForce(force, forceMode);
                }
                if (mapping.maxVelocityThreshold.HasValue && node.rigidbody.velocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    // there is some discussion about the "best" way to do this here
                    // https://answers.unity.com/questions/9985/limiting-rigidbody-velocity.html
                    node.rigidbody.velocity = node.rigidbody.velocity.normalized * mapping.maxVelocityThreshold.Value;
                }
            }

            if (node.articulationBody != null) {
                if (mapping.useLocalCoordinates) {
                    node.articulationBody.AddRelativeForce(force, forceMode);
                } else {
                    node.articulationBody.AddForce(force, forceMode);
                }
                if (mapping.maxVelocityThreshold.HasValue && node.articulationBody.velocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    node.articulationBody.velocity = node.articulationBody.velocity.normalized * mapping.maxVelocityThreshold.Value;
                }
            }

        }

        public static void AddTorque(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Torque' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;

            Vector3 torque = mapping.axis.Value.normalized * magnitude;

            //Debug.Log("AddTorque, torque: " + torque + " relative:" + mapping.useLocalCoordinates
            //    + " forceMode:" + ForceMode.Force);

            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;

            if (node.rigidbody != null) {
                if (mapping.useLocalCoordinates) {
                    node.rigidbody.AddRelativeTorque(torque, forceMode);
                } else {
                    node.rigidbody.AddTorque(torque, forceMode);
                }
                if (mapping.maxVelocityThreshold.HasValue && node.rigidbody.angularVelocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    Debug.Log($"Angular velocity {node.rigidbody.angularVelocity.magnitude} exceeds threshold {mapping.maxVelocityThreshold.Value}");
                    node.rigidbody.angularVelocity = node.rigidbody.angularVelocity.normalized * mapping.maxVelocityThreshold.Value;
                    Debug.Log($"Clamped angular velocity to {node.rigidbody.angularVelocity.magnitude}");
                }
            }
            if (node.articulationBody != null) {
                if (mapping.useLocalCoordinates) {
                    node.articulationBody.AddRelativeTorque(torque, forceMode);
                } else {
                    node.articulationBody.AddTorque(torque, forceMode);
                }
                if (mapping.maxVelocityThreshold.HasValue && node.articulationBody.angularVelocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    node.articulationBody.angularVelocity = node.articulationBody.angularVelocity.normalized * mapping.maxVelocityThreshold.Value;
                }
            }
        }

        public static void AddForceAtPosition(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.position.HasValue)
                throw new System.Exception("You need to provide a position to use the 'Add Force at Position' action.");
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Force at Position' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;
            Vector3 force = mapping.axis.Value.normalized * magnitude;

            //Debug.Log("AddForceAtPosition, force: " + force + "position" + mapping.position.Value
            //    + " relative:" + mapping.useLocalCoordinates + " forceMode:" + ForceMode.Force);

            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;

            if (node.rigidbody != null) {
                node.rigidbody.AddForceAtPosition(force, mapping.position.Value, forceMode);
                if (mapping.maxVelocityThreshold.HasValue && node.articulationBody.velocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    node.articulationBody.velocity = node.articulationBody.velocity.normalized * mapping.maxVelocityThreshold.Value;
                }
            }
            if (node.articulationBody != null) {
                node.articulationBody.AddForceAtPosition(force, mapping.position.Value, forceMode);
                if (mapping.maxVelocityThreshold.HasValue && node.articulationBody.velocity.magnitude > mapping.maxVelocityThreshold.Value) {
                    node.articulationBody.velocity = node.articulationBody.velocity.normalized * mapping.maxVelocityThreshold.Value;
                }
            }
        }

        public static void ChangePosition(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Change Position' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;
            Vector3 move = mapping.axis.Value.normalized * magnitude;
            if (mapping.useLocalCoordinates) {
                move = node.transform.TransformDirection(mapping.axis.Value.normalized) * magnitude;
            }
            //Debug.Log("ChangePosition, move: " + move + " relative:" + mapping.useLocalCoordinates);

            if (node.rigidbody != null) {
                node.rigidbody.MovePosition(node.rigidbody.position + move);
            }
            if (node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Change Position' action on an Articulation body.");
            }
        }

        public static void ChangeRotation(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Change Rotation' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;

            Vector3 rotate = mapping.axis.Value.normalized * magnitude;
            if (mapping.useLocalCoordinates) {
                rotate = node.transform.TransformDirection(mapping.axis.Value.normalized) * magnitude;
            }

            //Debug.Log("ChangeRotation, rotate: " + rotate + " relative:" + mapping.useLocalCoordinates);

            if (node.rigidbody != null) {
                node.rigidbody.MoveRotation(node.rigidbody.rotation * Quaternion.Euler(rotate));
            }
            if (node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Change Rotation' action on an Articulation body.");
            }
        }

        public static void SetPosition(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.position.HasValue)
                throw new System.Exception("You need to provide a position to use the 'Set Position' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;

            Vector3 position = mapping.position.Value * magnitude;
            if (mapping.useLocalCoordinates) {
                position = node.transform.TransformPoint(mapping.position.Value);
            }
            //Debug.Log("SetPosition, position: " + position);

            if (node.rigidbody != null) {
                node.rigidbody.MovePosition(position);
            }
            if (node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Set Position' action on an Articulation body.");
            }
        }

        public static void SetRotation(this Node node, float value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Set Rotation' action.");

            float magnitude = (value - mapping.offset) * mapping.amplitude;

            Vector3 axis = mapping.axis.Value;
            if (mapping.useLocalCoordinates) {
                axis = node.transform.TransformDirection(mapping.axis.Value);
            }
            //Debug.Log("SetRotation, axis: " + axis + " angle: " + magnitude);

            if (node.rigidbody != null) {
                node.rigidbody.MoveRotation(Quaternion.AngleAxis(magnitude, axis));
            }
            if (node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Set Rotation' action on an Articulation body.");
            }
        }
    }
}