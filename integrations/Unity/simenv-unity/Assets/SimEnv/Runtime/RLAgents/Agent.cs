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
            if (node.rigidbody == null && node.articulatedBody == null) {
                //  by default, if no rigidbody is present, add a simple character controller
                CharacterController cc = node.gameObject.AddComponent<CharacterController>();
                node.characterController = cc;
            }
        }
        void InitSensors() {
            // search children for Cameras and add these as camera sensors
            // this is a bit slow but it only runs once at startup
            foreach (Node node2 in Simulator.nodes.Values) {
                // search children for Cameras and create CameraSensors
                if (node2.camera != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    CameraSensor cameraSensor = new CameraSensor(node2.camera);
                    sensors.Add(cameraSensor);
                }
                // search children for StateSensors
                if (node2.sensor != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    sensors.Add(node2.sensor);
                }
            }

            // TODO: search children for RaycastSensors


        }

        void InitRewardFunctions() {
            Debug.Log("init reward functions");
            // find reward nodes with reward data
            var vals = Simulator.nodes.Values;
            foreach (Node node2 in Simulator.nodes.Values) {
                if (node2.rewardFunctionData != null
                && node2.gameObject.transform.IsChildOf(node.gameObject.transform)
                && node2.gameObject.transform.parent == node.transform) {
                    RewardFunction rewardFunction = RewardFunctionBuilder.Build(node2);
                    rewardFunctions.Add(rewardFunction);
                }
            }
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

        public class Data {
            public bool done;
            public float reward;
            public Dictionary<string, SensorBuffer> observations;
        }
    }
}