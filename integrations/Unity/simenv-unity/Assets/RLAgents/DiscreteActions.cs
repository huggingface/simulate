using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.Agents {
    public class DiscreteActions : Actions {
        public DiscreteActions(string name, string dist, List<string> available) : base(name, dist, available) {

        }

        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "discrete");
            Debug.Assert(stepAction.Count == 1, "in the discrete case step action must be of length 1");

            // in the case of discrete actions, this list is just one value
            // the value is casted to an int, this is a bit hacky and I am sure there is a more elegant way to do this.
            int iStepAction = (int)stepAction[0];
            // Clear previous actions
            forward = 0.0f;
            moveRight = 0.0f;
            turnRight = 0.0f;
            switch(available[iStepAction]) {
                case "move_forward":
                    forward = 1.0f;
                    break;
                case "move_backward":
                    forward = -1.0f;
                    break;
                case "move_left":
                    moveRight = 1.0f;
                    break;
                case "move_right":
                    moveRight = -1.0f;
                    break;
                case "turn_left":
                    turnRight = -1.0f;
                    break;
                case "turn_right":
                    turnRight = 1.0f;
                    break;
                default:
                    Debug.Assert(false, "invalid action");
                    break;
            }
        }
    }
}