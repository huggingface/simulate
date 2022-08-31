using System.Collections.Generic;
using UnityEngine;
using System;
using SimEnv.GLTF;

namespace SimEnv.RlAgents {
    public static class Actions {
        public static void ExecuteAction(this Agent agent, object action) {

            HFControllers.ActionMapping mapping = agent.actionSpace.GetMapping(action);
            List<float> value = new List<float> { 1f }; // TODO refactor when I (Ed) understand what this is
            switch (mapping.action) {
                case "add_force":
                    agent.AddForce(value, mapping);
                    break;
                case "add_relative_force":
                    agent.AddRelativeForce(value, mapping);
                    break;
                case "add_torque":
                    agent.AddTorque(value, mapping);
                    break;
                case "add_relative_torque":
                    agent.AddRelativeTorque(value, mapping);
                    break;
                case "add_force_at_position":
                    agent.AddForceAtPosition(value, mapping);
                    break;
                case "change_position":
                    agent.ChangePosition(value, mapping);
                    break;
                case "change_relative_position":
                    agent.ChangeRelativePosition(value, mapping);
                    break;
                case "change_rotation":
                    agent.ChangeRotation(value, mapping);
                    break;
                case "change_relative_rotation":
                    agent.ChangeRelativeRotation(value, mapping);
                    break;
            }
        }

        public static void AddForce(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude;
            agent.node.rigidbody.AddForce(force, ForceMode.Impulse);
        }

        public static void AddRelativeForce(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude;
            agent.node.rigidbody.AddRelativeForce(force, ForceMode.Impulse);
        }

        public static void AddTorque(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = mapping.axis.normalized * magnitude;
            agent.node.rigidbody.AddTorque(force, ForceMode.Impulse);
        }

        public static void AddRelativeTorque(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 force = agent.node.transform.TransformDirection(mapping.axis.normalized) * magnitude;
            agent.node.rigidbody.AddTorque(force, ForceMode.Impulse);
        }

        public static void AddForceAtPosition(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            throw new NotImplementedException();
        }

        public static void ChangePosition(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 move = mapping.axis.normalized * magnitude / MetaData.frameRate;
            agent.node.rigidbody.MovePosition(agent.node.transform.position + move);
        }

        public static void ChangeRelativePosition(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 move = agent.node.transform.TransformDirection(mapping.axis.normalized) * magnitude / MetaData.frameRate;
            Debug.Log(move.ToString());
            agent.node.rigidbody.MovePosition(agent.node.transform.position + move);
        }

        public static void ChangeRotation(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 rotate = mapping.axis.normalized * magnitude / MetaData.frameRate;
            agent.node.rigidbody.MoveRotation(agent.node.transform.rotation * Quaternion.Euler(rotate));
        }

        public static void ChangeRelativeRotation(this Agent agent, List<float> value, HFControllers.ActionMapping mapping) {
            if (value == null || value.Count != 1)
                throw new NotImplementedException();
            float magnitude = (value[0] - mapping.offset) * mapping.amplitude;
            if (mapping.lowerLimit.HasValue)
                magnitude = Mathf.Max(magnitude, mapping.lowerLimit.Value);
            if (mapping.upperLimit.HasValue)
                magnitude = Mathf.Min(magnitude, mapping.upperLimit.Value);
            Vector3 rotate = agent.node.transform.TransformDirection(mapping.axis.normalized) * magnitude / MetaData.frameRate;
            agent.node.rigidbody.MoveRotation(agent.node.transform.rotation * Quaternion.Euler(rotate));
        }
    }
}