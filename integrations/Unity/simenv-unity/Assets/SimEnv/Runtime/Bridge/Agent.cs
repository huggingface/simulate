using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace SimEnv {
    public abstract class Actions {
        public string name;
        public string dist;
        public List<string> available = new List<string>();
        public float forward = 0.0f;
        public float moveRight = 0.0f;
        public float turnRight = 0.0f;

        public abstract void SetAction(List<float> stepAction);
    }
    public class DiscreteActions : Actions {

        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "discrete", "not implemented");
            Debug.Assert(stepAction.Count == 1, "in the discrete case step action must be of length 1");

            // in the case of discrete actions, this list is just one value
            // the value is casted to an int, this is a bit hacky and I am sure there is a more elegant way to do this.
            int iStepAction = (int)stepAction[0];
            // Clear previous actions
            forward = 0.0f;
            moveRight = 0.0f;
            turnRight = 0.0f;
            switch (available[iStepAction]) {
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

    public class ContinuousActions : Actions {
        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "continuous", "not implemented");
            Debug.Assert(stepAction.Count == available.Count, "step action and avaiable count mismatch");

            for (int i = 0; i < stepAction.Count; i++) {
                switch (available[i]) {
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
            foreach (var avail in available) {
                Debug.Log("type: " + avail);
            }
        }
    }

    [RequireComponent(typeof(CharacterController))]
    public class Agent : MonoBehaviour {

        public float move_speed = 1f;
        public float turn_speed = 1f;
        public float height = 1f;

        private const bool HUMAN = false;

        public Color color = Color.white;

        CharacterController controller;

        void Awake() {
            controller = GetComponent<CharacterController>();
        }

        public Actions actions;
        // Start is called before the first frame update
        void Start() {

        }

        public void setProperties(SimEnv.GLTF.GLTF_agents.GLTFAgent agentData) {

            Debug.Log("Setting Agent properties");

            color = agentData.color;
            height = agentData.height;
            move_speed = agentData.move_speed;
            turn_speed = agentData.turn_speed;

            switch (agentData.action_dist) {

                case "discrete":
                    actions = new DiscreteActions();
                    break;
                case "continuous":
                    actions = new ContinuousActions();
                    break;
                default:
                    Debug.Assert(false, "action distribution was not discrete or continuous");
                    break;
            }

            actions.name = agentData.action_name;

            actions.dist = agentData.action_dist;
            actions.available = agentData.available_actions;

        }
        void Update() {

            if (HUMAN) {
                // Human control
                float x = Input.GetAxis("Horizontal");
                float z = Input.GetAxis("Vertical");
                float r = 0.0f;

                Vector3 move = transform.right * x + transform.forward * z;

                transform.Rotate(Vector3.up * r);
                if (Input.GetKeyUp("r")) {
                    Debug.Log("Agent reset");
                    transform.position = new Vector3(0.0f, 0.0f, 0.0f);
                }
            } else {
                // RL control
                Vector3 move = transform.right * actions.moveRight + transform.forward * actions.forward;
                controller.Move(move * move_speed * Time.deltaTime);
                float rotate = actions.turnRight;
                transform.Rotate(Vector3.up * rotate * turn_speed);
            }
        }

        public void SetAction(List<float> step_action) {
            actions.SetAction(step_action);
        }
    }


}