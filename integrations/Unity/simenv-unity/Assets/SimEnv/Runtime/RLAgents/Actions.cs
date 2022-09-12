using System.Collections.Generic;
using UnityEngine;
using System;
using SimEnv.GLTF;

namespace SimEnv.RlAgents {
    public static class Actions {
        public static void ExecuteAction(this Actor actor, object action) {
            HFActuators.ActionMapping mapping = actor.actionSpace.GetMapping(action);
            List<float> value = new List<float> { 1f }; // TODO refactor when I (Ed) understand what this is
            switch (mapping.action) {
                case "add_force":
                    actor.AddForce(value, mapping);
                    break;
                case "add_torque":
                    actor.AddTorque(value, mapping);
                    break;
                case "add_force_at_position":
                    actor.AddForceAtPosition(value, mapping);
                    break;
                case "change_position":
                    actor.ChangePosition(value, mapping);
                    break;
                case "change_rotation":
                    actor.ChangeRotation(value, mapping);
                    break;
                case "set_position":
                    actor.SetPosition(value, mapping);
                    break;
                case "set_rotation":
                    actor.SetRotation(value, mapping);
                    break;
                case "do_nothing":
                    break;
            }
        }

        public static void AddForce(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Force' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.maxVelocityThreshold.HasValue)
                if (actor.node.rigidbody.velocity.magnitude > mapping.maxVelocityThreshold.Value)
                    return;
            
            Vector3 force = mapping.axis.Value.normalized * magnitude;
            
            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;
            
            Debug.Log("AddForce, force: " + force + " relative:"
                + mapping.useLocalCoordinates + " isImpulse:" + mapping.isImpulse);

            if (actor.node.rigidbody != null) {
                if (mapping.useLocalCoordinates) {
                    actor.node.rigidbody.AddRelativeForce(force, forceMode);
                } else {
                    actor.node.rigidbody.AddForce(force, forceMode);
                }
            }

            if (actor.node.articulationBody != null) {
                if (mapping.useLocalCoordinates) {
                    actor.node.articulationBody.AddRelativeForce(force, forceMode);
                } else {
                    actor.node.articulationBody.AddForce(force, forceMode);
                }
            }

        }

        public static void AddTorque(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Torque' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();

            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.maxVelocityThreshold.HasValue)
                if (actor.node.rigidbody.angularVelocity.magnitude > mapping.maxVelocityThreshold.Value)
                    return;

            Vector3 torque = mapping.axis.Value.normalized * magnitude;

            Debug.Log("AddTorque, torque: " + torque + " relative:" + mapping.useLocalCoordinates
                + " forceMode:" + ForceMode.Force);

            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;
            
            if (actor.node.rigidbody != null) {
                if (mapping.useLocalCoordinates) {
                    actor.node.rigidbody.AddRelativeTorque(torque, forceMode);
                } else {
                    actor.node.rigidbody.AddTorque(torque, forceMode);
                }
            }
            if (actor.node.articulationBody != null) {
                if (mapping.useLocalCoordinates) {
                    actor.node.articulationBody.AddRelativeTorque(torque, forceMode);
                } else {
                    actor.node.articulationBody.AddTorque(torque, forceMode);
                }
            }
        }

        public static void AddForceAtPosition(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.position.HasValue)
                throw new System.Exception("You need to provide a position to use the 'Add Force at Position' action.");
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Add Force at Position' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();

            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.maxVelocityThreshold.HasValue)
                if (actor.node.rigidbody.velocity.magnitude > mapping.maxVelocityThreshold.Value)
                    return;

            Vector3 force = mapping.axis.Value.normalized * magnitude;

            Debug.Log("AddForceAtPosition, force: " + force + "position" + mapping.position.Value
                + " relative:" + mapping.useLocalCoordinates + " forceMode:" + ForceMode.Force);

            ForceMode forceMode = ForceMode.Force;
            if (mapping.isImpulse)
                forceMode = ForceMode.Impulse;
            
            if (actor.node.rigidbody != null) {
                actor.node.rigidbody.AddForceAtPosition(force, mapping.position.Value, forceMode);
            }
            if (actor.node.articulationBody != null) {
                actor.node.articulationBody.AddForceAtPosition(force, mapping.position.Value, forceMode);
            }
        }

        public static void ChangePosition(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Change Position' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            Vector3 move = mapping.axis.Value.normalized * magnitude;
            if (mapping.useLocalCoordinates) {
                move = actor.node.transform.TransformDirection(mapping.axis.Value.normalized) * magnitude;
            }
            Debug.Log("ChangePosition, move: " + move + " relative:" + mapping.useLocalCoordinates);

            if (actor.node.rigidbody != null) {
                actor.node.rigidbody.MovePosition(actor.node.rigidbody.position + move);
            }
            if (actor.node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Change Position' action on an Articulation body.");
            }
        }

        public static void ChangeRotation(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Change Rotation' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;

            Vector3 rotate = mapping.axis.Value.normalized * magnitude;
            if (mapping.useLocalCoordinates) {
                rotate = actor.node.transform.TransformDirection(mapping.axis.Value.normalized) * magnitude;
            }

            Debug.Log("ChangeRotation, rotate: " + rotate + " relative:" + mapping.useLocalCoordinates);

            if (actor.node.rigidbody != null) {
                actor.node.rigidbody.MoveRotation(actor.node.rigidbody.rotation * Quaternion.Euler(rotate));
            }
            if (actor.node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Change Rotation' action on an Articulation body.");
            }
        }

        public static void SetPosition(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.position.HasValue)
                throw new System.Exception("You need to provide a position to use the 'Set Position' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();

            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;

            Vector3 position = mapping.position.Value *  magnitude;
            if (mapping.useLocalCoordinates) {
                position = actor.node.transform.TransformPoint(mapping.position.Value);
            }
            Debug.Log("SetPosition, position: " + position);

            if (actor.node.rigidbody != null) {
                actor.node.rigidbody.MovePosition(position);
            }
            if (actor.node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Set Position' action on an Articulation body.");
            }
        }

        public static void SetRotation(this Actor actor, List<float> value, HFActuators.ActionMapping mapping) {
            if (!mapping.axis.HasValue)
                throw new System.Exception("You need to provide an axis to use the 'Set Rotation' action.");
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
        
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;

            Vector3 axis = mapping.axis.Value;
            if (mapping.useLocalCoordinates) {
                axis = actor.node.transform.TransformDirection(mapping.axis.Value);
            }
            Debug.Log("SetRotation, axis: " + axis + " angle: " + magnitude);

            if (actor.node.rigidbody != null) {
                actor.node.rigidbody.MoveRotation(Quaternion.AngleAxis(magnitude, axis));
            }
            if (actor.node.articulationBody != null) {
                throw new System.Exception("You cannot use 'Set Rotation' action on an Articulation body.");
            }
        }
    }
}