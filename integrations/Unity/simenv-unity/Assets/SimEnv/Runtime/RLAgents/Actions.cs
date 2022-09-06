using System.Collections.Generic;
using UnityEngine;
using System;
using SimEnv.GLTF;

namespace SimEnv.RlAgents {
    public static class Actions {
        public static void ExecuteAction(this Actor actor, object action) {
            HFControllers.ActionMapping mapping = actor.actionSpace.GetMapping(action);
            List<float> value = new List<float> { 1f }; // TODO refactor when I (Ed) understand what this is
            switch (mapping.action) {
                case "add_force":
                    actor.AddForce(value, mapping);
                    break;
                case "add_relative_force":
                    actor.AddRelativeForce(value, mapping);
                    break;
                case "add_torque":
                    actor.AddTorque(value, mapping);
                    break;
                case "add_relative_torque":
                    actor.AddRelativeTorque(value, mapping);
                    break;
                case "add_force_at_position":
                    actor.AddForceAtPosition(value, mapping);
                    break;
                case "change_position":
                    actor.ChangePosition(value, mapping);
                    break;
                case "change_relative_position":
                    actor.ChangeRelativePosition(value, mapping);
                    break;
                case "change_rotation":
                    actor.ChangeRotation(value, mapping);
                    break;
                case "change_relative_rotation":
                    actor.ChangeRelativeRotation(value, mapping);
                    break;
            }
        }

        public static void AddForce(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude * Time.fixedDeltaTime;
            actor.node.rigidbody.AddForce(force, ForceMode.Acceleration);
        }

        public static void AddRelativeForce(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude * Time.fixedDeltaTime;
            actor.node.rigidbody.AddRelativeForce(force, ForceMode.Acceleration);
        }

        public static void AddTorque(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude * Time.fixedDeltaTime;
            actor.node.rigidbody.AddTorque(force, ForceMode.Acceleration);
        }

        public static void AddRelativeTorque(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = actor.node.transform.TransformDirection(mapping.axis.normalized) * magnitude * Time.fixedDeltaTime;
            actor.node.rigidbody.AddTorque(force, ForceMode.Acceleration);
        }

        public static void AddForceAtPosition(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            throw new NotImplementedException();
        }

        public static void ChangePosition(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 move = mapping.axis.normalized * magnitude / MetaData.instance.frameRate;
            actor.node.rigidbody.MovePosition(actor.node.transform.position + move);
        }

        public static void ChangeRelativePosition(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 move = actor.node.transform.TransformDirection(mapping.axis.normalized) * magnitude / MetaData.instance.frameRate;
            actor.node.rigidbody.MovePosition(actor.node.transform.position + move);
        }

        public static void ChangeRotation(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 rotate = mapping.axis.normalized * magnitude / MetaData.instance.frameRate;
            actor.node.rigidbody.MoveRotation(actor.node.transform.rotation * Quaternion.Euler(rotate));
        }

        public static void ChangeRelativeRotation(this Actor actor, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 rotate = actor.node.transform.TransformDirection(mapping.axis.normalized) * magnitude / MetaData.instance.frameRate;
            actor.node.rigidbody.MoveRotation(actor.node.transform.rotation * Quaternion.Euler(rotate));
        }
    }
}