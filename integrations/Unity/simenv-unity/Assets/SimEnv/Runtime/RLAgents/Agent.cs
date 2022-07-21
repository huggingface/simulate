using System.Collections.Generic;
using UnityEngine;
using System.Collections;
using SimEnv.RlActions;
using SimEnv.GLTF;

namespace SimEnv.RlAgents {
    public class Agent {
        public Node node;
        public Rigidbody body;
        public RlAction actions;
        private List<string> obsDeviceNames = new List<string>();
        private List<RenderCamera> obsDevices = new List<RenderCamera>();
        private List<RewardFunction> rewardFunctions = new List<RewardFunction>();

        // TODO check and update in particular with reset
        private const bool HUMAN = false;
        private float accumReward = 0.0f;
        private Vector3 originalPosition;

        // TODO remove
        // private const float radius = .25f;
        // public RenderCamera cam;

        public Agent(Node node, HFRlAgents.HFRlAgentsComponent agentData) {
            this.node = node;
            node.referenceObject = this;
            node.tag = "Agent";
            SetProperties(agentData);
            //AgentManager.instance.Register(this);
        }

        public void Initialize() {
            // We setup the rigid body
            body = node.gameObject.GetComponent<Rigidbody>();

            // We connect the observation devices to the agent now that the whole scene is imported
            foreach (string obsDeviceName in obsDeviceNames) {
                Debug.Log("Finding obs device" + obsDeviceName);
                Node cameraNode = GameObject.Find(obsDeviceName).GetComponent<Node>();

                if (cameraNode != null) {
                    Debug.Log("Adding observation device " + obsDeviceName + cameraNode.renderCamera);
                    obsDevices.Add(cameraNode.renderCamera);
                } else {
                    Debug.LogError("Could not find observation device " + obsDeviceName);
                }
            }
            // actions.Print();
        }

        public RewardFunction GetRewardFunction(HFRlAgents.HFRlAgentsReward reward) {
            // Debug.Log("Creating reward function");
            // get the shared properties
            // Debug.Log("Finding entity_a " + reward.entity_a);
            // Debug.Log("Finding entity_b " + reward.entity_b);
            GameObject entity_a = GameObject.Find(reward.entity_a);
            GameObject entity_b = GameObject.Find(reward.entity_b);

            if (entity_a == null) {
                Debug.LogWarning("Failed to find entity_a " + reward.entity_a);
            }
            if (entity_b == null) {
                Debug.LogWarning("Failed to find entity_b " + reward.entity_b);
            }
            IDistanceMetric distanceMetric = null; // refactor this to a reward factory?
            RewardFunction rewardFunction = null;

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
                    rewardFunction = new RewardFunctionAnd(
                        GetRewardFunction(reward.reward_function_a), GetRewardFunction(reward.reward_function_b), 
                            entity_a, entity_b, distanceMetric);
                    break;
                
                case "or":
                    rewardFunction = new RewardFunctionOr(
                        GetRewardFunction(reward.reward_function_a), GetRewardFunction(reward.reward_function_b), 
                            entity_a, entity_b, distanceMetric);
                    break;

                case "xor":
                    rewardFunction = new RewardFunctionXor(
                        GetRewardFunction(reward.reward_function_a), GetRewardFunction(reward.reward_function_b), 
                            entity_a, entity_b, distanceMetric);
                    break;
                
                case "not":
                    rewardFunction = new RewardFunctionNot(
                        GetRewardFunction(reward.reward_function_a), entity_a, entity_b, distanceMetric);
                    break;

                default:
                    Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                    break;
        }
        return rewardFunction;
    }

        public void SetProperties(HFRlAgents.HFRlAgentsComponent agentData) {
            // Debug.Log("Setting Agent properties");

            originalPosition = node.transform.localPosition;

            // Store pointers to all our observation devices
            obsDeviceNames = agentData.observations;
            if (obsDeviceNames.Count != 1) {
                Debug.LogError("More or less than one observation device not implemented yet.");
            }

            // Create our agent actions
            HFRlAgents.HFRlAgentsActions gl_act = agentData.actions;
            switch (gl_act.type) {
                case "MappedDiscrete":
                    actions = new MappedDiscreteAction(
                        n: gl_act.n,
                        physics: gl_act.physics,
                        amplitudes: gl_act.amplitudes,
                        clip_low: gl_act.clip_low,
                        clip_high: gl_act.clip_high);
                    break;
                case "MappedBox":
                    actions = new MappedContinuousAction(
                        low: gl_act.low,
                        high: gl_act.high,
                        shape: gl_act.shape,
                        dtype: gl_act.dtype,
                        physics: gl_act.physics,
                        scaling: gl_act.scaling,
                        offset: gl_act.offset,
                        clip_low: gl_act.clip_low,
                        clip_high: gl_act.clip_high);
                    break;
                default:
                    Debug.Assert(false, "We currently only support MappedDiscrete and MappedBox actions");
                    break;
            }

            // TODO(thom, dylan, ed) Do we want to emulate this at some point?
            // controller.slopeLimit = 45;
            // controller.stepOffset = .3f;
            // controller.skinWidth = .08f;
            // controller.minMoveDistance = .001f;
            // controller.center = Vector3.y * height / 2f;
            // controller.radius = radius;
            // controller.height = height;
            // SetupModel();

            // add the reward functions to the agent
            List<HFRlAgents.HFRlAgentsReward> gl_rewardFunctions = agentData.rewards;
            foreach (var reward in gl_rewardFunctions) {
                RewardFunction rewardFunction = GetRewardFunction(reward);
                rewardFunctions.Add(rewardFunction);
            }
        }

        public void AgentUpdate(float frameRate) {
            float timeStep = 1.0f / frameRate;
            if (HUMAN) {
                // Human control
                float x = Input.GetAxis("Horizontal");
                float z = Input.GetAxis("Vertical");
                float r = 0.0f;

                Vector3 positionOffset = new Vector3(x, 0, z);
                Quaternion rotation = Quaternion.Euler(0, r, 0);

                Vector3 newPosition = body.position + node.gameObject.transform.TransformDirection(positionOffset);
                Quaternion newRotation = body.rotation * rotation;

                body.MovePosition(newPosition);
                body.MoveRotation(newRotation);

                if (Input.GetKeyUp("r")) {
                    // Debug.Log("Agent reset");
                    body.MovePosition(Vector3.zero);
                    body.MoveRotation(Quaternion.identity);
                }
            } else {
                // RL control
                if (actions.positionOffset != Vector3.zero) {
                    // Debug.Log("Position offset: " + actions.positionOffset);
                    Vector3 newPosition = body.position + node.gameObject.transform.TransformDirection(actions.positionOffset * timeStep);
                    // Debug.Log("body.position: " + body.position);
                    // Debug.Log("newPosition: " + newPosition);
                    body.MovePosition(newPosition);
                }
                if (actions.rotation != Vector3.zero) {
                    // Debug.Log("Rotation offset: " + actions.rotation);
                    Quaternion newRotation = body.rotation * Quaternion.Euler(actions.rotation * timeStep);
                    // Debug.Log("body.rotation: " + body.rotation);
                    // Debug.Log("newRotation: " + newRotation);
                    body.MoveRotation(newRotation);
                }
                if (actions.velocity != Vector3.zero) {
                    // Debug.Log("Velocity change: " + actions.velocity);
                    Vector3 localForce = node.gameObject.transform.TransformDirection(actions.velocity * timeStep);
                    body.AddRelativeForce(localForce);
                }
                if (actions.torque != Vector3.zero) {
                    // Debug.Log("Torque change: " + actions.torque);
                    Vector3 localTorque = node.gameObject.transform.TransformDirection(actions.torque * timeStep);
                    body.AddRelativeTorque(localTorque);
                }
            }
        }

        public void UpdateReward() {
            accumReward += CalculateReward();
        }

        public void Reset() {
            accumReward = 0.0f;
            // Reset the agent
            node.gameObject.transform.localPosition = originalPosition;


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

        public int getObservationSizes() {
            return obsDevices[0].getObservationSizes();
        }

        public int[] getObservationShape() {
            return obsDevices[0].getObservationShape();
        }

        public IEnumerator GetObservationCoroutine(uint[] pixelValues, int startingIndex) {
            yield return obsDevices[0].RenderCoroutine(colors => {
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