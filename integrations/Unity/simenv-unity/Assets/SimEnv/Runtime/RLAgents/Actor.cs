using System.Collections.Generic;
using UnityEngine;
using SimEnv.GLTF;
using System.Linq;

namespace SimEnv.RlAgents {
    public class Actor {
        public Node node { get; private set; }
        public HFActuators.ActionSpace actionSpace { get; private set; }

        private Dictionary<string, object> observations = new Dictionary<string, object>();

        public List<ISensor> sensors = new List<ISensor>();
        List<RewardFunction> rewardFunctions = new List<RewardFunction>();
        float accumReward;
        object currentAction;

        public Actor(Node node) {
            this.node = node;
            node.gameObject.tag = "Actor";
            Initialize();
        }

        void Initialize() {
            Debug.Log("initializing Actor");

            InitActions();
            InitSensors();
            InitRewardFunctions();

            Simulator.BeforeIntermediateFrame += HandleIntermediateFrame;
        }

        void InitActions() {
            if (node.actionData == null) {
                Debug.LogWarning("Actor missing action data");
                return;
            }
            if (node.actionData.n == null && node.actionData.low == null) {
                Debug.LogWarning("At least one action space required.");
                return;
            }

            if (node.actionData.n != null) {
                // Discrete action space
                actionSpace = new HFActuators.ActionSpace(node.actionData);
            } else if (node.actionData.low != null) {
                // continuous action space
                Debug.LogWarning("Continous actions are yet to be implemented");
                return;
            } else {
                Debug.LogWarning("Error parsing actor action space");
                return;
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

        public void SetAction(object action) {
            this.currentAction = action;
        }

        public Data GetEventData() {
            UpdateReward();
            bool done = IsDone();
            float reward = GetReward();
            ZeroReward();
            // Observations not included, as they are read later from the camera
            Data data = new Data() {
                done = done,
                reward = reward,
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

        public void ReadSensorObservations(Data data, Dictionary<string, Buffer> sensorBuffers, int mapIndex, int actorIndex) {
            Dictionary<string, Buffer> observations = new Dictionary<string, Buffer>();
            foreach (var sensor in sensors) {
                observations[sensor.GetName()] = sensor.GetObs(sensorBuffers[sensor.GetName()], mapIndex, actorIndex);
            }
            data.observations = observations;
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
            public Dictionary<string, Buffer> observations;
        }
    }
}