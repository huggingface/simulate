using System.Collections.Generic;
using UnityEngine;
using SimEnv.GLTF;
using System.Linq;

namespace SimEnv.RlAgents {
    public class Agent {
        public Node node { get; private set; }
        public HFControllers.ActionSpace actionSpace { get; private set; }

        private Dictionary<string, object> observations = new Dictionary<string, object>();

        private List<ISensor> sensors = new List<ISensor>();
        List<RewardFunction> rewardFunctions = new List<RewardFunction>();
        float accumReward;
        object currentAction;

        public Agent(Node node) {
            this.node = node;
            node.gameObject.tag = "Agent";
            Initialize();
        }

        void Initialize() {
            Debug.Log("initializing agent");

            InitActions();
            InitSensors();
            InitRewardFunctions();




            // if (node.agentData.box_actions == null && node.agentData.discrete_actions == null) {
            //     Debug.LogWarning("At least one action space required.");
            //     return;
            // }
            // if (node.agentData.box_actions != null)
            //     actionSpace = node.actionData.box_actions;
            // else if (node.agentData.discrete_actions != null)
            //     actionSpace = node.agentData.discrete_actions;

            // rewardFunctions = new List<RewardFunction>();
            // if (node.agentData.reward_functions != null) {
            //     foreach (HFRlAgents.HFRlAgentsReward reward in node.agentData.reward_functions) {
            //         if (!TryGetRewardFunction(reward, out RewardFunction rewardFunction)) {
            //             Debug.LogWarning("Failed to get reward function");
            //             continue;
            //         }
            //         rewardFunctions.Add(rewardFunction);
            //     }
            // }

            Simulator.BeforeIntermediateFrame += HandleIntermediateFrame;
        }

        void InitActions() {
            if (node.actionData == null) {
                Debug.LogWarning("Agent missing action data");
                return;
            }
            if (node.actionData.n == null && node.actionData.low == null) {
                Debug.LogWarning("At least one action space required.");
                return;
            }

            if (node.actionData.n != null) {
                // Discrete action space
                actionSpace = new HFControllers.ActionSpace(node.actionData);
            } else if (node.agentData.discrete_actions != null) {
                // continuous action space
                Debug.LogWarning("Continous actions are yet to be implemented");
                return;
            } else {
                Debug.LogWarning("Error parsing agent action space");
                return;
            }
        }
        void InitSensors() {
            // search children for Cameras and add these as camera sensors
            // this is a bit slow but it only runs once at startup
            foreach (Node node2 in Simulator.nodes.Values) {
                if (node2.camera != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    CameraSensor cameraSensor = new CameraSensor(node2.camera);
                    sensors.Add(cameraSensor);
                }
                if (node2.sensor != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    sensors.Add(node2.sensor);
                }
            }

            // search children for StateSensors


            // search children for RaycastSensors


        }

        void InitRewardFunctions() {

        }


        void HandleIntermediateFrame() {
            if (node == null || node.gameObject == null) {
                Simulator.BeforeIntermediateFrame -= HandleIntermediateFrame;
                return;
            }
            if (currentAction != null && node.gameObject.activeSelf)
                this.ExecuteAction(currentAction);
        }

        public void Step(object action) {
            this.currentAction = action;
        }

        public Data GetEventData() {
            UpdateReward();
            bool done = IsDone();
            float reward = GetReward();
            ZeroReward();
            Dictionary<string, SensorBuffer> observations = null;
            // no need to render if the environment is done, frames will be taken from the next map
            if (!done) {
                observations = GetSensorObservations();
            }
            Data data = new Data() {
                done = done,
                reward = reward,
                observations = observations,
            };

            return data;
        }

        public void EnableSensors() {
            foreach (var sensor in sensors) {
                sensor.Enable();
            }
        }

        public void DisableSensors() {
            foreach (var sensor in sensors) {
                sensor.Disable();
            }
        }

        Dictionary<string, SensorBuffer> GetSensorObservations() {
            Dictionary<string, SensorBuffer> observations = new Dictionary<string, SensorBuffer>();
            foreach (var sensor in sensors) {
                observations[sensor.GetName()] = sensor.GetObs();

            }
            return observations;
        }


        Dictionary<string, uint[,,]> GetCameraObservations() {
            Dictionary<string, uint[,,]> cameras = new Dictionary<string, uint[,,]>();
            foreach (string cameraName in node.agentData.camera_sensors.Select(x => x.camera)) {
                if (!Simulator.nodes.TryGetValue(cameraName, out Node cameraNode) || cameraNode.camera == null) {
                    Debug.LogWarning($"Couldn't find camera {cameraName}");
                    continue;
                }
                cameraNode.camera.CopyRenderResultToBuffer(out uint[,,] buffer);
                cameraNode.camera.camera.enabled = false;
                cameras.Add(cameraName, buffer);
            }
            return cameras;
        }

        public void UpdateReward() {
            accumReward += CalculateReward();
        }

        public void Reset() {
            accumReward = 0.0f;
            foreach (RewardFunction rewardFunction in rewardFunctions)
                rewardFunction.Reset();
        }

        public float CalculateReward() {
            float reward = 0.0f;
            foreach (RewardFunction rewardFunction in rewardFunctions)
                reward += rewardFunction.CalculateReward();
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
                } else if (rewardFunction is RewardFunctionPredicate) {
                    var rewardFunctionPredicate = rewardFunction as RewardFunctionPredicate;
                    done = done | (rewardFunctionPredicate.hasTriggered && rewardFunctionPredicate.isTerminal);
                }
            }
            return done;
        }

        public bool TryGetRewardFunction(HFRlAgents.HFRlAgentsReward reward, out RewardFunction rewardFunction) {
            rewardFunction = null;
            if (!Simulator.nodes.TryGetValue(reward.entity_a, out Node entity_a)) {
                Debug.LogWarning($"Failed to find node {reward.entity_a}");
                return false;
            }
            if (!Simulator.nodes.TryGetValue(reward.entity_b, out Node entity_b)) {
                Debug.LogWarning($"Failed to find node {reward.entity_b}");
                return false;
            }

            IDistanceMetric distanceMetric = null; // refactor this to a reward factory?
            switch (reward.distance_metric) {
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

            switch (reward.type) {
                case "dense":
                    rewardFunction = new DenseRewardFunction(
                        entity_a, entity_b, distanceMetric, reward.scalar
                    );
                    break;
                case "sparse":
                    rewardFunction = new SparseRewardFunction(
                        entity_a, entity_b, distanceMetric, reward.scalar, reward.threshold, reward.is_terminal, reward.is_collectable, reward.trigger_once);
                    break;
                case "timeout":
                    rewardFunction = new TimeoutRewardFunction(
                        entity_a, entity_b, distanceMetric, reward.scalar, reward.threshold, reward.is_terminal, reward.is_collectable, reward.trigger_once);
                    break;
                case "and":
                    if (!TryGetRewardFunction(reward.reward_function_a, out RewardFunction a) || !TryGetRewardFunction(reward.reward_function_b, out RewardFunction b))
                        return false;
                    rewardFunction = new RewardFunctionAnd(
                        a, b, entity_a, entity_b, distanceMetric, reward.is_terminal);
                    break;

                case "or":
                    if (!TryGetRewardFunction(reward.reward_function_a, out a) || !TryGetRewardFunction(reward.reward_function_b, out b))
                        return false;
                    rewardFunction = new RewardFunctionOr(
                        a, b, entity_a, entity_b, distanceMetric, reward.is_terminal);
                    break;

                case "xor":
                    if (!TryGetRewardFunction(reward.reward_function_a, out a) || !TryGetRewardFunction(reward.reward_function_b, out b))
                        return false;
                    rewardFunction = new RewardFunctionXor(
                        a, b, entity_a, entity_b, distanceMetric, reward.is_terminal);
                    break;

                case "not":
                    if (!TryGetRewardFunction(reward.reward_function_a, out a))
                        return false;
                    rewardFunction = new RewardFunctionNot(
                        a, entity_a, entity_b, distanceMetric, reward.is_terminal);
                    break;

                case "see":
                    rewardFunction = new SeeRewardFunction(
                        entity_a, entity_b, distanceMetric, reward.scalar, reward.threshold, reward.is_terminal,
                        reward.is_collectable, reward.trigger_once);
                    break;

                default:
                    Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                    break;
            }

            return true;
        }

        public class Data {
            public bool done;
            public float reward;
            public Dictionary<string, SensorBuffer> observations;
        }
    }
}