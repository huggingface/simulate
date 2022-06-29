using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
using System.Collections;

namespace SimEnv.Agents {
    public static class JsonHelper {
        public static T[] FromJson<T>(string json) {
            Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
            return wrapper.Items;
        }

        public static string ToJson<T>(T[] array) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.Items = array;
            return JsonUtility.ToJson(wrapper);
        }

        public static string ToJson<T>(T[] array, bool prettyPrint) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.Items = array;
            return JsonUtility.ToJson(wrapper, prettyPrint);
        }

        [Serializable]
        private class Wrapper<T> {
            public T[] Items;
        }
    }

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
            Debug.Assert(dist == "discrete");
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
            Debug.Assert(dist == "continuous");
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

    public class Agent {
        public float move_speed = 1f;

        private Vector3 originalPosition;
        public float turn_speed = 1f;
        public float height = 1f;

        private const float radius = .25f;
        private const bool HUMAN = false;

        private float accumReward = 0.0f;

        public Color color = Color.white;
        private List<RewardFunction> rewardFunctions = new List<RewardFunction>();

        public Node node;
        public RenderCamera cam;

        CharacterController controller;

        public Actions actions;

        public Agent(Node node, HFRlAgentsRlComponent agentData) {
            this.node = node;
            SetProperties(agentData);
            AgentManager.instance.Register(this);
        }

        public void SetProperties(HFRlAgentsRlComponent agentData) {
            Debug.Log("Setting Agent properties");
            originalPosition = new Vector3(node.gameObject.transform.position.x, node.gameObject.transform.position.y, node.gameObject.transform.position.z);
            color = new Color(agentData.color[0], agentData.color[1], agentData.color[2]);
            height = agentData.height;
            move_speed = agentData.move_speed;
            turn_speed = agentData.turn_speed;

            foreach (Transform child in node.gameObject.transform) {
                if (child.gameObject.name == "Capsule") {
                    child.gameObject.GetComponent<MeshRenderer>().material.color = color;
                    break;
                }
            }

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

            // set up components
            controller = node.gameObject.AddComponent<CharacterController>();
            controller.slopeLimit = 45;
            controller.stepOffset = .3f;
            controller.skinWidth = .08f;
            controller.minMoveDistance = .001f;
            controller.center = Vector3.up * height / 2f;
            controller.radius = radius;
            controller.height = height;
            SetupModel();

            //
            // add the reward functions to the agent
            for (int i = 0; i < agentData.reward_functions.Count; i++) {
                Debug.Log("Creating reward function");
                // get the shared properties
                Debug.Log("Finding entity_a " + agentData.reward_entity1s[i]);
                Debug.Log("Finding entity_b " + agentData.reward_entity2s[i]);
                GameObject entity_a = GameObject.Find(agentData.reward_entity1s[i]);

                GameObject entity_b = GameObject.Find(agentData.reward_entity2s[i]);
                if (entity_a == null) {
                    Debug.Log("Failed to find entity_a " + agentData.reward_entity1s[i]);
                }
                if (entity_b == null) {
                    Debug.Log("Failed to find entity_b " + agentData.reward_entity2s[i]);
                }
                IDistanceMetric distanceMetric = null; // refactor this to a reward factory?
                RewardFunction rewardFunction = null;

                switch (agentData.reward_distance_metrics[i]) {
                    case "euclidean":
                        distanceMetric = new EuclideanDistance();
                        break;
                    case "cosine":
                        distanceMetric = new CosineDistance();
                        break;
                    default:
                        Debug.Assert(false, "incompatable distance metric provided, chose from (euclidean, cosine)");
                        break;
                }

                switch (agentData.reward_functions[i]) {
                    case "dense":
                        rewardFunction = new DenseRewardFunction(
                            entity_a, entity_b, distanceMetric, agentData.reward_scalars[i]
                        );
                        break;
                    case "sparse":
                        rewardFunction = new SparseRewardFunction(
                            entity_a, entity_b, distanceMetric, agentData.reward_scalars[i], agentData.reward_thresholds[i], agentData.reward_is_terminals[i]);
                        break;
                    case "timeout":
                        rewardFunction = new TimeoutRewardFunction(
                            entity_a, entity_b, distanceMetric, agentData.reward_scalars[i], agentData.reward_thresholds[i], agentData.reward_is_terminals[i]);
                        break;

                    default:
                        Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                        break;
                }

                rewardFunctions.Add(rewardFunction);
            }
        }

        void SetupModel() {
            GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            capsule.name = "Capsule";
            capsule.transform.SetParent(node.gameObject.transform);
            capsule.transform.localPosition = Vector3.up * height / 2f;
            capsule.transform.localScale = new Vector3(radius * 2f, height / 2f, radius * 2f);
            MeshRenderer capsuleRenderer = capsule.GetComponent<MeshRenderer>();
            capsuleRenderer.material = Resources.Load<Material>("DefaultLit");
            capsuleRenderer.material.color = color;
            capsule.GetComponent<Collider>().enabled = false;
        }

        public void AgentUpdate() {
            if (HUMAN) {
                // Human control
                float x = Input.GetAxis("Horizontal");
                float z = Input.GetAxis("Vertical");
                float r = 0.0f;

                Vector3 move = node.gameObject.transform.right * x + node.gameObject.transform.forward * z;

                node.gameObject.transform.Rotate(Vector3.up * r);
                if (Input.GetKeyUp("r")) {
                    Debug.Log("Agent reset");
                    node.gameObject.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
                }
            } else {
                // RL control
                Vector3 move = node.gameObject.transform.right * actions.moveRight + node.gameObject.transform.forward * actions.forward;
                controller.Move(move * move_speed * Time.deltaTime);
                float rotate = actions.turnRight;
                node.gameObject.transform.Rotate(Vector3.up * rotate * turn_speed);
            }
        }

        public void UpdateReward() {
            accumReward += CalculateReward();
        }

        public void Reset() {
            accumReward = 0.0f;
            // Reset the agent
            controller.enabled = false; // the Character Controller takes control of the tranform and must be disabled
            node.gameObject.transform.position = originalPosition;
            controller.enabled = true;


            // Reset reward objects?
            // Reset reward functions

            foreach (RewardFunction rewardFunction in rewardFunctions) {
                rewardFunction.Reset();
            }
        }

        public float CalculateReward() {
            float reward = 0.0f;

            foreach (RewardFunction rewardFunction in rewardFunctions) {
                reward += rewardFunction.CalculateReward();
            }
            return reward;
        }

        public float GetReward() {
            return accumReward;
        }
        public void ZeroReward() {
            accumReward = 0.0f;
        }

        public bool IsDone() {
            // TODO: currently the reward functions identify which objects correspond to terminal states
            // Implement: episode termination
            bool done = false;
            foreach (RewardFunction rewardFunction in rewardFunctions) {
                if (rewardFunction is SparseRewardFunction) {
                    var sparseRewardFunction = rewardFunction as SparseRewardFunction;
                    done = done | (sparseRewardFunction.hasTriggered && sparseRewardFunction.isTerminal);
                }
            }

            return done;
        }

        public IEnumerator GetObservationCoroutine(uint[] pixelValues, int startingIndex) {
            yield return cam.RenderCoroutine(colors => {
                for (int i = 0; i < colors.Length; i++) {
                    pixelValues[startingIndex + i * 3] = colors[i].r;
                    pixelValues[startingIndex + i * 3 + 1] = colors[i].g;
                    pixelValues[startingIndex + i * 3 + 2] = colors[i].b;
                }
            });
        }

        public void SetAction(List<float> step_action) {
            actions.SetAction(step_action);
        }
    }
}