using UnityEngine;
using System;

namespace SimEnv.RlAgents {
    public interface IDistanceMetric {
        public float Calculate(Node e1, Node e2);
    }

    public class EuclideanDistance : IDistanceMetric {
        public float Calculate(Node e1, Node e2) {
            return Vector3.Distance(e1.transform.position, e2.transform.position);
        }
    }

    public class CosineDistance : IDistanceMetric {
        public float Calculate(Node e1, Node e2) {
            return Vector3.Dot(e1.transform.position.normalized, e2.transform.position.normalized);
        }
    }

    public abstract class RewardFunction {
        public Node entityA;
        public Node entityB;
        public float rewardScalar = 1.0f;
        public IDistanceMetric distanceMetric;
        public abstract void Reset();
        public abstract float CalculateReward();
    }

    public class DenseRewardFunction : RewardFunction {
        float bestDistance = float.PositiveInfinity;

        public DenseRewardFunction(Node entityA, Node entityB, IDistanceMetric distanceMetric, float rewardScalar) {
            base.entityA = entityA;
            base.entityB = entityB;
            this.distanceMetric = distanceMetric;
            this.rewardScalar = rewardScalar;
        }

        public override void Reset() {
            bestDistance = distanceMetric.Calculate(entityA, entityB);
        }

        public override float CalculateReward() {
            float distance = distanceMetric.Calculate(entityA, entityB);

            float reward = 0.0f;

            if (distance < bestDistance) {
                reward += bestDistance - distance;
                bestDistance = distance;
            }

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

    public abstract class RewardFunctionPredicate : RewardFunction {
        // TODO: works in the assumption that A and B has the same reward
        public RewardFunction rewardFunctionA;
        public RewardFunction rewardFunctionB = null;
        public bool hasTriggered = false;
        public bool isTerminal = false;
        public RewardFunctionPredicate(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                Node entityA, Node entityB, IDistanceMetric distanceMetric, bool isTerminal) {
            this.rewardFunctionA = rewardFunctionA;
            this.rewardFunctionB = rewardFunctionB;
            this.entityA = entityA;
            this.entityB = entityB;
            this.distanceMetric = distanceMetric;
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
                Node entity_a, Node entity_b, IDistanceMetric distanceMetric, bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, entity_a, entity_b, distanceMetric, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Min(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }

    }

    public class RewardFunctionOr : RewardFunctionPredicate {
        public RewardFunctionOr(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                Node entityA, Node entityB, IDistanceMetric distanceMetric, bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, entityA, entityB, distanceMetric, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Max(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionXor : RewardFunctionPredicate {
        public RewardFunctionXor(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB,
                Node entityA, Node entityB, IDistanceMetric distanceMetric, bool isTerminal)
                : base(rewardFunctionA, rewardFunctionB, entityA, entityB, distanceMetric, isTerminal) { }

        public override float CalculateReward() {
            float reward = Math.Abs(rewardFunctionA.CalculateReward() - rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionNot : RewardFunctionPredicate {
        // TODO: works in the assumption that A is sparse
        public RewardFunctionNot(RewardFunction rewardFunctionA,
                Node entityA, Node entityB, IDistanceMetric distanceMetric, bool isTerminal)
                : base(rewardFunctionA, null, entityA, entityB, distanceMetric, isTerminal) { }

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
