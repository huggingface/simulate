using System.Collections.Generic;
using System.Threading.Tasks;
using ISimEnv;
using SimEnv.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class Agent : IAgent {
        public Node node;
        public RenderCamera camera;
        public Actions actions;
        public CharacterController controller;
        public float height;
        public float radius;
        public float moveSpeed;
        public float turnSpeed;

        List<RewardFunction> rewardFunctions;
        float accumReward;

        public Agent(Node node, HF_RL_agents.HF_RL_Agent data) {
            this.node = node;
            height = data.height;
            radius = .5f;
            moveSpeed = data.move_speed;
            turnSpeed = data.turn_speed;
            rewardFunctions = new List<RewardFunction>();
            SetProperties(data);
            AgentManager.instance.Register(this);
        }

        public void Step() {
            Vector3 move = node.transform.right * actions.moveRight + node.transform.forward * actions.forward;
            controller.Move(move * moveSpeed * Time.deltaTime);
            float rotate = actions.turnRight;
            node.transform.Rotate(Vector3.up * rotate * turnSpeed);
        }

        public void UpdateReward() {
            accumReward += CalculateReward();
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

        public void Reset() {
            accumReward = 0;
            foreach (RewardFunction rewardFunction in rewardFunctions)
                rewardFunction.Reset();
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

        public void GetObservation(UnityAction<IAgentObservation> callback) {
            camera.Render(buffer => {
                callback(new AgentImageObservation(buffer));
            });
        }

        public void SetAction(List<float> step_action) {
            actions.SetAction(step_action);
        }

        void SetProperties(HF_RL_agents.HF_RL_Agent data) {
            controller = node.gameObject.AddComponent<CharacterController>();
            controller.slopeLimit = 45;
            controller.stepOffset = .3f;
            controller.skinWidth = .08f;
            controller.minMoveDistance = .001f;
            controller.center = Vector3.up * height / 2f;
            controller.radius = radius;
            controller.height = height;

            GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            capsule.name = "Capsule";
            capsule.transform.SetParent(node.transform);
            capsule.transform.localPosition = Vector3.up * height / 2f;
            capsule.transform.localScale = new Vector3(radius * 2f, height / 2f, radius * 2f);
            capsule.GetComponent<MeshRenderer>().sharedMaterial = Resources.Load<Material>("AgentMaterial");

            switch(data.action_dist) {
                case "discrete":
                    actions = new DiscreteActions(data.action_name, data.action_dist, data.available_actions);
                    break;
                case "continuous":
                    actions = new ContinuousActions(data.action_name, data.action_dist, data.available_actions);
                    break;
                default:
                    throw new System.ArgumentException("Action distribution not discrete or continuous");
            }

            // add the reward functions to the agent
            for(int i = 0; i < data.reward_functions.Count; i++) {
                Debug.Log("Creating reward function");
                // get the shared properties
                Debug.Log("Finding entity1 " + data.reward_entity1s[i]);
                Debug.Log("Finding entity2 " + data.reward_entity2s[i]);
                GameObject entity1 = GameObject.Find(data.reward_entity1s[i]);
                GameObject entity2 = GameObject.Find(data.reward_entity2s[i]);
                if(entity1 == null)
                    Debug.LogWarning("Failed to find entity1 " + data.reward_entity1s[i]);
                if(entity2 == null)
                    Debug.LogWarning("Failed to find entity2 " + data.reward_entity2s[i]);
                IDistanceMetric distanceMetric = null; // refactor this to a reward factory?
                RewardFunction rewardFunction = null;

                switch(data.reward_distance_metrics[i]) {
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

                switch(data.reward_functions[i]) {
                    case "dense":
                        rewardFunction = new DenseRewardFunction(
                            entity1, entity2, distanceMetric, data.reward_scalars[i]
                        );
                        break;
                    case "sparse":
                        rewardFunction = new SparseRewardFunction(
                            entity1, entity2, distanceMetric, data.reward_scalars[i], data.reward_thresholds[i], data.reward_is_terminals[i]
                        );
                        break;

                    default:
                        Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                        break;
                }

                rewardFunctions.Add(rewardFunction);
            }
        }
    }
}