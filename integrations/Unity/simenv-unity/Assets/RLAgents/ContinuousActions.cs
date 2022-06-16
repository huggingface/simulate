using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.Agents {
    public class ContinuousActions : Actions {
        public ContinuousActions(string name, string dist, List<string> available) : base(name, dist, available) {

        }

        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "continuous");
            Debug.Assert(stepAction.Count == available.Count, "step action and avaiable count mismatch");

            for(int i = 0; i < stepAction.Count; i++) {
                switch(available[i]) {
                    case "move_forward_backward":
                        forward = stepAction[i];
                        break;
                    case "move_left_right":
                        moveRight = stepAction[i];
                        break;
                    case "turn_left_right":
                        turnRight = stepAction[i];
                        break;
                    default:
                        Debug.Assert(false, "invalid action");
                        break;
                }
            }
        }

        public void Print() {
            Debug.Log("Printing actions");
            Debug.Log("name: " + name);
            Debug.Log("dist: " + dist);
            Debug.Log("name: " + name);
            foreach(var avail in available) {
                Debug.Log("type: " + avail);
            }
        }
    }
}