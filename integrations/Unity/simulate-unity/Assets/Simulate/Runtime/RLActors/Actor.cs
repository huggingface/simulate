using System.Collections.Generic;
using UnityEngine;
using Simulate.GLTF;

namespace Simulate.RlAgents {
    public class Actor {
        public Node node { get; private set; }

        private Dictionary<string, object> observations = new Dictionary<string, object>();

        public List<ISensor> sensors = new List<ISensor>();
        public Dictionary<string, Node> actuatorNodes = new Dictionary<string, Node>();
        List<RewardFunction> rewardFunctions = new List<RewardFunction>();
        float accumReward;
        public Dictionary<string, List<float>> currentAction = new Dictionary<string, List<float>>();

        public Actor(Node node) {
            this.node = node;
            Initialize();
        }

        void Initialize() {
            InitActions();
            InitSensors();
            InitRewardFunctions();

            Simulator.BeforeIntermediateFrame += HandleIntermediateFrame;
        }

        void InitActions() {
            if (node.actuatorData == null) {
                Debug.LogWarning("Actor missing actuator data");
                return;
            }
            if (node.actuatorData.n == null && node.actuatorData.low == null) {
                Debug.LogWarning("At least one action space required.");
                return;
            }

            // search children for Actuators
            // this is a bit slow but it only runs once at startup
            foreach (Node node2 in Simulator.nodes.Values) {
                if (node2.actuator != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    actuatorNodes[node2.actuator.actuator_tag] = node2;
                }
            }


        }
        void InitSensors() {
            // search children for Cameras and add these as camera sensors
            // this is a bit slow but it only runs once at startup
            foreach (Node node2 in Simulator.nodes.Values) {
                // search children for Cameras and create CameraSensors
                if (node2.camera != null && node2.gameObject.transform.IsChildOf(node.gameObject.transform)) {
                    Debug.Log("Found camera sensor: " + node2.name);
                    Debug.Log("Found camera data: " + node2.cameraData);
                    Debug.Log("Found camera data extra: " + node2.cameraData.extras);
                    Debug.Log("Found camera data extra sensor tag: " + node2.cameraData.extras.sensor_tag);
                    CameraSensor cameraSensor = new CameraSensor(node2.camera, node2.cameraData.extras.sensor_tag);
                    sensors.Add(cameraSensor);
                }
                // search children for StateSensors
                if (RLPlugin.sensors.TryGetValue(node2.name, out ISensor sensor) && node2.transform.IsChildOf(node.transform)) {
                    sensors.Add(sensor);
                }
            }
            // TODO: search children for RaycastSensors
        }

        void InitRewardFunctions() {
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

            if (currentAction.Count > 0 && node.gameObject.activeSelf)
                this.ExecuteAction(currentAction);
        }

        public void SetAction(Dictionary<string, List<float>> action) {
            this.currentAction = action;
        }

        public (float, bool) GetRewardDone() {
            UpdateReward();
            bool done = IsDone();
            float reward = GetReward();
            ZeroReward();
            // Observations not included, as they are read later from the camera
            return (reward, done);
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

        public void ReadSensorObservations(Dictionary<string, Buffer> sensorBuffers, int bufferIndex) {
            foreach (var sensor in sensors) {
                sensor.AddObsToBuffer(sensorBuffers[sensor.GetName()], bufferIndex);
            }
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

        // public class Data {
        //     public bool done;
        //     public float reward;
        //     public Dictionary<string, Buffer> observations;
        // }
    }
}