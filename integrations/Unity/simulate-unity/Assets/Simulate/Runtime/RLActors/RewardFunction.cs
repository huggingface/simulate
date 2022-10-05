using UnityEngine;
using System.Collections.Generic;
using System;

namespace Simulate.RlAgents {
    public interface IDistanceMetric {
        public float Calculate(Node e1, Node e2);
        public void Reset(Node e1, Node e2);
    }

    public class EuclideanDistance : IDistanceMetric {
        public float Calculate(Node e1, Node e2) {
            return Vector3.Distance(e1.transform.position, e2.transform.position);
        }
        public void Reset(Node e1, Node e2) { }
    }

    public class CosineDistance : IDistanceMetric {
        public float Calculate(Node e1, Node e2) {
            return Vector3.Dot(e1.transform.position.normalized, e2.transform.position.normalized);
        }
        public void Reset(Node e1, Node e2) { }
    }

    public class BestDistance : IDistanceMetric {

        private float bestDistance = float.PositiveInfinity;
        private IDistanceMetric distanceMetric;

        public BestDistance(IDistanceMetric distanceMetric) {
            this.distanceMetric = distanceMetric;
        }

        public float Calculate(Node e1, Node e2) {
            float reward = 0.0f;
            float distance = distanceMetric.Calculate(e1, e2);
            if (distance < bestDistance) {
                reward += bestDistance - distance;
                bestDistance = distance;
            }
            return reward;
        }

        public void Reset(Node e1, Node e2) {
            bestDistance = distanceMetric.Calculate(e1, e2);
        }


    }

    public static class RewardFunctionBuilder {
        public static readonly string[] LEAF_REWARD_FUNCTION_TYPES = { "dense", "sparse", "timeout", "see", "angle_to" };
        public static readonly string[] NODE_REWARD_FUNCTION_TYPES = { "and", "or", "not", "xor" };
        public static RewardFunction Build(Node node) {
            Debug.Assert(node.rewardFunctionData != null);


            if (Array.Exists(LEAF_REWARD_FUNCTION_TYPES, element => element == node.rewardFunctionData.type)) {
                return buildLeafRewardFunction(node);
            }
            if (Array.Exists(NODE_REWARD_FUNCTION_TYPES, element => element == node.rewardFunctionData.type)) {
                return buildNodeRewardFunction(node);
            }
            return null;
        }

        public static RewardFunction buildLeafRewardFunction(Node node) {
            RewardFunction rewardFunction = null;
            Simulate.GLTF.HFRewardFunctions.HFRewardFunction rewardData = node.rewardFunctionData;
            Node entity_a = null;
            Node entity_b = null;

            if (rewardData.entity_a != null && Simulator.nodes.ContainsKey(rewardData.entity_a)) {
                entity_a = Simulator.nodes[rewardData.entity_a];
            }
            if (rewardData.entity_b != null && Simulator.nodes.ContainsKey(rewardData.entity_b)) {
                entity_b = Simulator.nodes[rewardData.entity_b];
            }

            IDistanceMetric distanceMetric = null; // refactor this to a reward factory?
            switch (rewardData.distance_metric) {
                case "euclidean":
                    distanceMetric = new EuclideanDistance();
                    break;
                case "best_euclidean":
                    distanceMetric = new BestDistance(new EuclideanDistance());
                    break;
                case "cosine":
                    distanceMetric = new CosineDistance();
                    break;
                default:
                    Debug.LogWarning($"WARNING incompatable distance metric provided for reward of type {rewardData.type}");
                    break;
            }

            switch (rewardData.type) {
                case "dense":
                    rewardFunction = new DenseRewardFunction(
                        entity_a, entity_b, distanceMetric, rewardData.scalar
                    );
                    break;
                case "sparse":
                    rewardFunction = new SparseRewardFunction(
                        entity_a, entity_b, distanceMetric, rewardData.scalar, rewardData.threshold, rewardData.is_terminal, rewardData.is_collectable, rewardData.trigger_once);
                    break;
                case "timeout":
                    rewardFunction = new TimeoutRewardFunction(
                        entity_a, entity_b, distanceMetric, rewardData.scalar, rewardData.threshold, rewardData.is_terminal, rewardData.is_collectable, rewardData.trigger_once);
                    break;
                case "see":
                    rewardFunction = new SeeRewardFunction(
                        entity_a, entity_b, distanceMetric, rewardData.scalar, rewardData.threshold, rewardData.is_terminal,
                        rewardData.is_collectable, rewardData.trigger_once);
                    break;
                case "angle_to":
                    rewardFunction = new AngleToRewardFunction(
                        entity_a, entity_b, distanceMetric, rewardData.scalar, rewardData.direction, rewardData.threshold, rewardData.is_terminal,
                        rewardData.is_collectable, rewardData.trigger_once);
                    break;

                default:
                    Debug.Assert(false, "incompatable distance metric provided, chose from (euclidian, cosine)");
                    break;
            }

            return rewardFunction;
        }

        public static RewardFunction buildNodeRewardFunction(Node node) {
            RewardFunction rewardFunction = null;
            Simulate.GLTF.HFRewardFunctions.HFRewardFunction rewardData = node.rewardFunctionData;
            // I(Ed) do not like my implementation here, potentially slow. Perhaps Dylan can help ? TODO
            List<Node> children = new List<Node>();
            foreach (Node node2 in Simulator.nodes.Values) {
                if (node2.rewardFunctionData != null
                && node2.gameObject.transform.IsChildOf(node.gameObject.transform)
                && node2.gameObject.transform.parent == node.transform) {
                    children.Add(node2);
                }
            }

            switch (rewardData.type) {
                case "and":
                    Debug.Assert(children.Count == 2);
                    rewardFunction = new RewardFunctionAnd(
                                 RewardFunctionBuilder.Build(children[0]),
                                 RewardFunctionBuilder.Build(children[1]),
                                 rewardData.is_terminal
                    );
                    break;

                case "or":
                    Debug.Assert(children.Count == 2);
                    rewardFunction = new RewardFunctionOr(
                        RewardFunctionBuilder.Build(children[0]),
                        RewardFunctionBuilder.Build(children[1]),
                        rewardData.is_terminal
                    );
                    break;

                case "xor":
                    Debug.Assert(children.Count == 2);
                    rewardFunction = new RewardFunctionXor(
                        RewardFunctionBuilder.Build(children[0]),
                        RewardFunctionBuilder.Build(children[1]),
                        rewardData.is_terminal
                    );
                    break;

                case "not":
                    Debug.Assert(children.Count == 1);
                    rewardFunction = new RewardFunctionNot(
                        RewardFunctionBuilder.Build(children[0]),
                        rewardData.is_terminal
                    );
                    break;
                default:
                    Debug.Assert(false, "incompatable reward function provided, chose from (euclidian, cosine)");
                    break;
            }
            return rewardFunction;
        }
    }

    public abstract class RewardFunction {
        public Node entityA;
        public Node entityB;
        public Vector3 direction;
        public float rewardScalar = 1.0f;
        public IDistanceMetric distanceMetric;
        public abstract void Reset();
        public abstract float CalculateReward();
    }

    public class DenseRewardFunction : RewardFunction {

        public DenseRewardFunction(Node entityA, Node entityB, IDistanceMetric distanceMetric, float rewardScalar) {
            base.entityA = entityA;
            base.entityB = entityB;
            this.distanceMetric = distanceMetric;
            this.rewardScalar = rewardScalar;
        }

        public override void Reset() {
            distanceMetric?.Reset(entityA, entityB);
        }

        public override float CalculateReward() {
            float reward = distanceMetric.Calculate(entityA, entityB);
            return reward * rewardScalar;
        }
    }

    public class SparseRewardFunction : RewardFunction {
        public bool hasTriggered = false;
        public bool isTerminal = false;
        public float threshold = 1.0f;
        public bool isCollectable = false;
        public bool triggerOnce = true;

        public SparseRewardFunction(Node entityA, Node entityB, IDistanceMetric distanceMetric,
            float rewardScalar, float threshold, bool isTerminal, bool isCollectable, bool triggerOnce) {
            base.entityA = entityA;
            base.entityB = entityB;
            this.distanceMetric = distanceMetric;
            this.threshold = threshold;
            this.isTerminal = isTerminal;
            this.rewardScalar = rewardScalar;
            this.isCollectable = isCollectable;
            this.triggerOnce = triggerOnce;
        }

        public override void Reset() {
            hasTriggered = false;
            if (isCollectable) {
                entityB.gameObject.SetActive(true);
            }
            distanceMetric?.Reset(entityA, entityB);
        }

        public override float CalculateReward() {
            float reward = 0.0f;
            float distance = distanceMetric.Calculate(entityA, entityB);
            if ((!hasTriggered || !triggerOnce) && (distance < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
                if (isCollectable) {
                    entityB.gameObject.SetActive(false);
                }
            }
            return reward;
        }
    }

    public class SeeRewardFunction : SparseRewardFunction {
        public SeeRewardFunction(Node entityA, Node entityB,
            IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal, bool isCollectable, bool triggerOnce)
                : base(entityA, entityB, distanceMetric, rewardScalar, threshold, isTerminal, isCollectable, triggerOnce) { }

        public override float CalculateReward() {
            float reward = 0.0f;

            // Get angle in degrees and then compare to the threshold
            float angle = Vector3.Angle(entityA.transform.position - entityB.transform.position, entityA.transform.forward);

            if ((!hasTriggered || !triggerOnce) && (angle < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
                if (isCollectable) {
                    entityB.gameObject.SetActive(false);
                }
            }

            return reward;
        }
    }

    public class AngleToRewardFunction : SparseRewardFunction {
        public AngleToRewardFunction(Node entityA, Node entityB,
            IDistanceMetric distanceMetric, float rewardScalar, Vector3 direction, float threshold, bool isTerminal, bool isCollectable, bool triggerOnce)
                : base(entityA, entityB, distanceMetric, rewardScalar, threshold, isTerminal, isCollectable, triggerOnce) {
            this.direction = direction;
        }

        public override float CalculateReward() {
            float reward = 0.0f;

            // Get angle in degrees and then compare to the threshold
            float angle = Vector3.Angle(entityA.transform.position - entityB.transform.position, direction);
            if ((!hasTriggered || !triggerOnce) && (angle < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
                if (isCollectable) {
                    entityB.gameObject.SetActive(false);
                }
            }

            return reward;
        }
    }

    public abstract class RewardFunctionPredicate : RewardFunction {
        // TODO: works in the assumption that A and B has the same reward
        public RewardFunction rewardFunctionA;
        public RewardFunction rewardFunctionB = null;
        public bool hasTriggered = false;
        public bool isTerminal = false;
        public RewardFunctionPredicate(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, bool isTerminal) {
            this.rewardFunctionA = rewardFunctionA;
            this.rewardFunctionB = rewardFunctionB;
            this.isTerminal = isTerminal;
        }

        public override void Reset() {
            hasTriggered = false;
            rewardFunctionA.Reset();
            if (rewardFunctionB != null) {
                rewardFunctionB.Reset();
            }
        }
    }

    public class RewardFunctionAnd : RewardFunctionPredicate {
        public RewardFunctionAnd(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Min(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }

    }

    public class RewardFunctionOr : RewardFunctionPredicate {
        public RewardFunctionOr(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Max(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionXor : RewardFunctionPredicate {
        public RewardFunctionXor(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                 bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Abs(rewardFunctionA.CalculateReward() - rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionNot : RewardFunctionPredicate {
        // TODO: works in the assumption that A is sparse
        public RewardFunctionNot(RewardFunction rewardFunctionA,
                bool isTerminal)
                : base(rewardFunctionA, null, isTerminal) { }

        public override float CalculateReward() {
            float reward = 0.0f;
            if (!(rewardFunctionA.CalculateReward() > 0.0f)) {
                hasTriggered = true;
                reward += rewardFunctionA.rewardScalar;
            }
            return reward;
        }
    }

    public class TimeoutRewardFunction : SparseRewardFunction {
        int steps = 0;

        public TimeoutRewardFunction(Node entityA, Node entityB,
            IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal, bool isCollectable, bool triggerOnce)
                : base(entityA, entityB, distanceMetric, rewardScalar, threshold, isTerminal, isCollectable, triggerOnce) { }

        public override void Reset() {
            hasTriggered = false;
            steps = 0;
        }

        public override float CalculateReward() {
            float reward = 0.0f;
            steps += 1;
            if (!hasTriggered && (steps > threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
            }
            return reward * rewardScalar;
        }
    }
}
