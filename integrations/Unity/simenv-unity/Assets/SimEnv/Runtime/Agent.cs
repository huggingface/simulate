using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
using System.Collections;
using SimEnv.RlActions;
using SimEnv.GLTF.HFRlAgents;

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


    public class Agent {
        public Node node;
        public Rigidbody body;
        public RlAction actions;
        private List<Node> observations = new List<Node>();
        private List<RewardFunction> rewardFunctions = new List<RewardFunction>();

        // TODO check and update in particular with reset
        private const bool HUMAN = false;
        private float accumReward = 0.0f;
        private Vector3 originalPosition;

        // TODO remove
        // private const float radius = .25f;
        // public RenderCamera cam;

        public Agent(Node node, HFRlAgentsComponent agentData, List<Node> observationDevices) {
            this.node = node;
            SetProperties(agentData, observationDevices);
            AgentManager.instance.Register(this);
        }

        public void SetProperties(HFRlAgentsComponent agentData, List<Node> observationDevices) {
            Debug.Log("Setting Agent properties");

            originalPosition = node.transform.position;

            // Store pointers to all our observation devices
            observations = observationDevices;
            if (observations.Count > 1) {
                Debug.Log("More than one observation device not implemented yet.");
            }

            // Create our agent actions
            HFRlAgentsActions gl_act = agentData.actions;
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

            // set up rigidbody component
            body = node.gameObject.AddComponent<Rigidbody>();

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
            List<HFRlAgentsReward> gl_rewardFunctions = agentData.rewards;
            foreach (var reward in gl_rewardFunctions) {
                Debug.Log("Creating reward function");
                // get the shared properties
                Debug.Log("Finding entity_a " + reward.entity_a);
                Debug.Log("Finding entity_b " + reward.entity_b);
                GameObject entity_a = GameObject.Find(reward.entity_a);

                GameObject entity_b = GameObject.Find(reward.entity_b);
                if (entity_a == null) {
                    Debug.Log("Failed to find entity_a " + reward.entity_a);
                }
                if (entity_b == null) {
                    Debug.Log("Failed to find entity_b " + reward.entity_b);
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
                            entity_a, entity_b, distanceMetric, reward.scalar, reward.threshold, reward.is_terminal);
                        break;
                    case "timeout":
                        rewardFunction = new TimeoutRewardFunction(
                            entity_a, entity_b, distanceMetric, reward.scalar, reward.threshold, reward.is_terminal);
                        break;

                    default:
                        Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                        break;
                }

                rewardFunctions.Add(rewardFunction);
            }
        }

        public void AgentUpdate() {
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
                    Debug.Log("Agent reset");
                    body.MovePosition(Vector3.zero);
                    body.MoveRotation(Quaternion.identity);
                }
            } else {
                // RL control
                if (actions.positionOffset != Vector3.zero) {
                    Vector3 newPosition = body.position + node.gameObject.transform.TransformDirection(actions.positionOffset);
                    body.MovePosition(newPosition);
                }
                if (actions.rotation != Quaternion.identity) {
                    Quaternion newRotation = body.rotation * actions.rotation;
                    body.MoveRotation(newRotation);
                }
                if (actions.velocity != Vector3.zero) {
                    Vector3 localForce = node.gameObject.transform.TransformDirection(actions.velocity);
                    body.AddRelativeForce(localForce);
                }
                if (actions.torque != Vector3.zero) {
                    Vector3 localTorque = node.gameObject.transform.TransformDirection(actions.torque);
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
            node.gameObject.transform.position = originalPosition;


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
            if (observations.Count > 0 && observations[0].camera != null) {
                int observationSize = observations[0].camera.getObservationSizes();
                return observationSize;
            }
            return 0;
        }

        public IEnumerator GetObservationCoroutine(uint[] pixelValues, int startingIndex) {
            if (observations.Count > 0 && observations[0].camera != null) {
                int observationSize = observations[0].camera.getObservationSizes();
                return observationSize;
            }
            yield return (RenderCamera) observations[0].camera.RenderCoroutine(colors => {
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