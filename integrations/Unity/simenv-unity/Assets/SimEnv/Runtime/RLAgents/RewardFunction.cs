using UnityEngine;
using System;

namespace SimEnv.RlAgents {
    public interface IDistanceMetric {
        public float Calculate(GameObject e1, GameObject e2);
    }

    public class EuclideanDistance : IDistanceMetric {
        public float Calculate(GameObject e1, GameObject e2) {
            return Vector3.Distance(e1.transform.position, e2.transform.position);

        }
    }
    public class CosineDistance : IDistanceMetric {
        public float Calculate(GameObject e1, GameObject e2) {
            // TODO
            return Vector3.Distance(e1.transform.position, e2.transform.position);

        }
    }
    public abstract class RewardFunction {
        public GameObject entity_a;
        public GameObject entity_b;
        public float rewardScalar = 1.0f;
        public IDistanceMetric distanceMetric;
        public abstract void Reset();
        public abstract float CalculateReward();

    }

    public class DenseRewardFunction : RewardFunction {
        float bestDistance = float.PositiveInfinity;

        public override void Reset() {
            bestDistance = distanceMetric.Calculate(entity_a, entity_b);
        }
        public DenseRewardFunction(GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, float rewardScalar) {
            this.entity_a = entity_a;
            this.entity_b = entity_b;
            this.distanceMetric = distanceMetric;
            this.rewardScalar = rewardScalar;
        }
        public override float CalculateReward() {
            float distance = distanceMetric.Calculate(entity_a, entity_b);

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
        public SparseRewardFunction(GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal, bool isCollectable, bool triggerOnce) {
            this.entity_a = entity_a;
            this.entity_b = entity_b;
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
                entity_b.SetActive(true);
            }
        }

        public override float CalculateReward() {
            float reward = 0.0f;
            float distance = distanceMetric.Calculate(entity_a, entity_b);
            if ((!hasTriggered || !triggerOnce) && (distance < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
                if (isCollectable) {
                    entity_b.SetActive(false);
                }
            }
            return reward * rewardScalar;
        }
    }

    public abstract class RewardFunctionPredicate : RewardFunction {
        // TODO: works in the assumption that A and B has the same reward
        public RewardFunction rewardFunctionA;
        public RewardFunction rewardFunctionB = null;
        public bool hasTriggered = false;
        public bool isTerminal = false;
        public RewardFunctionPredicate(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, 
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, bool isTerminal) {
            this.rewardFunctionA = rewardFunctionA;
            this.rewardFunctionB = rewardFunctionB;
            this.entity_a = entity_a;
            this.entity_b = entity_b;
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
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, bool isTerminal) :
            base(rewardFunctionA, rewardFunctionB, entity_a, entity_b, distanceMetric, isTerminal) {}

        public override float CalculateReward() {
            float reward = Math.Min(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
        
    }

    public class RewardFunctionOr : RewardFunctionPredicate{
        public RewardFunctionOr(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, 
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, bool isTerminal) :
            base(rewardFunctionA, rewardFunctionB, entity_a, entity_b, distanceMetric, isTerminal) {}

        public override float CalculateReward() {
            float reward = Math.Max(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionXor : RewardFunctionPredicate {
        public RewardFunctionXor(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, 
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, bool isTerminal) :
            base(rewardFunctionA, rewardFunctionB, entity_a, entity_b, distanceMetric, isTerminal) {}

        public override float CalculateReward() {
            float reward = Math.Abs(rewardFunctionA.CalculateReward() - rewardFunctionB.CalculateReward());
            if (reward > 0.0f) hasTriggered = true;
            return reward;
        }
    }

    public class RewardFunctionNot : RewardFunctionPredicate {
        // TODO: works in the assumption that A is sparse
        public RewardFunctionNot(RewardFunction rewardFunctionA,
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric,
                bool isTerminal) :
            base(rewardFunctionA, null, entity_a, entity_b, distanceMetric, isTerminal) {}

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

        public TimeoutRewardFunction(GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal, bool isCollectable, 
                                    bool triggerOnce) :
                base(entity_a, entity_b, distanceMetric, rewardScalar, threshold, isTerminal, isCollectable, triggerOnce) { }
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
