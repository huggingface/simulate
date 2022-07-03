using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
using System.Collections;

namespace SimEnv.RlActions {
    public abstract class RlAction {
        protected List<string> physics;
        protected List<float> clip_low = new List<float>();
        protected List<float> clip_high = new List<float>();

        public Vector3 positionOffset = Vector3.zero;
        public Vector3 rotation = Vector3.zero;
        public Vector3 velocity = Vector3.zero;
        public Vector3 torque = Vector3.zero;

        protected void ResetVectors() {
            positionOffset = Vector3.zero;
            rotation = Vector3.zero;
            velocity = Vector3.zero;
            torque = Vector3.zero;
        }

        public abstract void SetAction(List<float> stepAction);

        public void Print() {
            Debug.Log("Printing actions");
            Debug.Log(" - type: " + this.GetType().Name
                    + " - physics: " + physics
                    + " - clip_low: " + clip_low
                    + " - clip_high: " + clip_high);
        }
    }

    public class MappedDiscreteAction : RlAction {
        protected int n;
        protected List<float> amplitudes;
        public MappedDiscreteAction(int n, List<string> physics,
                List<float> amplitudes, List<float> clip_low, List<float> clip_high) {
            this.n = n;
            this.physics = physics;
            this.amplitudes = amplitudes;
            this.clip_low = clip_low;
            this.clip_high = clip_high;
        }

        private float CheckBounds(int iStepAction, float value) {
            if (clip_low.Count > iStepAction) {
                value = Math.Max(value, clip_low[iStepAction]);
            }
            if (clip_high.Count > iStepAction) {
                value = Math.Min(value, clip_high[iStepAction]);
            }
            return value;
        }

        public override void SetAction(List<float> stepAction) {
            Debug.Assert(stepAction.Count == 1, "in the discrete case step action must be of length 1");

            // Clear previous actions
            ResetVectors();

            for (int i = 0; i <stepAction.Count; i++) {
                // the action value is casted to an int, this is a bit hacky and I am sure there is a more elegant way to do this.
                int iStepAction = (int)stepAction[0];
                string physicsAction = physics[iStepAction];
                float physicsAmplitude = amplitudes[iStepAction];
                switch (physicsAction) {
                    case "position_x":
                        positionOffset.x = CheckBounds(iStepAction, positionOffset.x + physicsAmplitude);
                        break;
                    case "position_y":
                        positionOffset.y = CheckBounds(iStepAction, positionOffset.y + physicsAmplitude);
                        break;
                    case "position_z":
                        positionOffset.z = CheckBounds(iStepAction, positionOffset.z + physicsAmplitude);
                        break;
                    case "rotation_x":
                        rotation.x = CheckBounds(iStepAction, rotation.x + physicsAmplitude);
                        break;
                    case "rotation_y":
                        rotation.y = CheckBounds(iStepAction, rotation.y + physicsAmplitude);
                        break;
                    case "rotation_z":
                        rotation.z = CheckBounds(iStepAction, rotation.z + physicsAmplitude);
                        break;
                    case "velocity_x":
                        velocity.x = CheckBounds(iStepAction, velocity.x + physicsAmplitude);
                        break;
                    case "velocity_y":
                        velocity.y = CheckBounds(iStepAction, velocity.y + physicsAmplitude);
                        break;
                    case "velocity_z":
                        velocity.z = CheckBounds(iStepAction, velocity.z + physicsAmplitude);
                        break;
                    case "angular_velocity_x":
                        torque.x = CheckBounds(iStepAction, torque.x + physicsAmplitude);
                        break;
                    case "angular_velocity_y":
                        torque.y = CheckBounds(iStepAction, torque.y + physicsAmplitude);
                        break;
                    case "angular_velocity_z":
                        torque.z = CheckBounds(iStepAction, torque.z + physicsAmplitude);
                        break;
                    default:
                        Debug.Assert(false, "invalid action");
                        break;
                }
            }
        }
    }

    public class MappedContinuousAction : RlAction {
        protected List<float> low = new List<float>();
        protected List<float> high = new List<float>();
        protected List<int> shape;
        protected string dtype;
        protected List<float> scaling = new List<float>();
        protected List<float> offset = new List<float>();

        public MappedContinuousAction(List<float> low, List<float> high, List<int> shape,
                string dtype, List<string> physics, List<float> scaling, List<float> offset,
                List<float> clip_low, List<float> clip_high) {
            this.low = low;
            this.high = high;
            this.shape = shape;
            this.dtype = dtype;
            this.physics = physics;
            this.scaling = scaling;
            this.offset = offset;
            this.clip_low = clip_low;
            this.clip_high = clip_high;

            if (clip_low.Count > 1 || clip_high.Count > 1) {
                Debug.Assert(false, "clip_low and clip_high must be of length 1");
            }
            if (scaling.Count > 1 || offset.Count > 1) {
                Debug.Assert(false, "scaling and offset lists longer than 1 unsupported at the moment");  // TODO support
            }
        }

        private float ConvertValue(float previous, float increment) {
            float value = previous + scaling[0] * (increment - offset[0]);
            if (clip_low.Count > 0) {
                value = Mathf.Max(value, clip_low[0]);
            }
            if (clip_high.Count > 0) {
                value = Mathf.Min(value, clip_high[0]);
            }
            return value;
        }

        public override void SetAction(List<float> stepAction) {
            ResetVectors();
            string physicsAction = physics[0];
            for (int i = 0; i <stepAction.Count; i++) {
                switch (physicsAction) {
                    case "position_x":
                        positionOffset.x = ConvertValue(positionOffset.x, stepAction[i]);
                        break;
                    case "position_y":
                        positionOffset.y = ConvertValue(positionOffset.y, stepAction[i]);
                        break;
                    case "position_z":
                        positionOffset.z = ConvertValue(positionOffset.z, stepAction[i]);
                        break;
                    case "rotation_x":
                        rotation.x = ConvertValue(rotation.x, stepAction[i]);
                        break;
                    case "rotation_y":
                        rotation.y = ConvertValue(rotation.y, stepAction[i]);
                        break;
                    case "rotation_z":
                        rotation.z = ConvertValue(rotation.z, stepAction[i]);
                        break;
                    case "velocity_x":
                        velocity.x = ConvertValue(velocity.x, stepAction[i]);
                        break;
                    case "velocity_y":
                        velocity.y = ConvertValue(velocity.y, stepAction[i]);
                        break;
                    case "velocity_z":
                        velocity.z = ConvertValue(velocity.z, stepAction[i]);
                        break;
                    case "angular_velocity_x":
                        torque.x = ConvertValue(torque.x, stepAction[i]);
                        break;
                    case "angular_velocity_y":
                        torque.y = ConvertValue(torque.y, stepAction[i]);
                        break;
                    case "angular_velocity_z":
                        torque.z = ConvertValue(torque.z, stepAction[i]);
                        break;
                    default:
                        Debug.Assert(false, "invalid action");
                        break;
                }
            }
        }
    }
}