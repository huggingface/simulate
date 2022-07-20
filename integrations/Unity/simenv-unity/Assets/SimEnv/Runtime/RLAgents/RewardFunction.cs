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

    public class RewardFunctionAnd : RewardFunction {
        // TODO: works in the assumption that A and B has the same reward
        public RewardFunction rewardFunctionA;
        public RewardFunction rewardFunctionB;

        public RewardFunctionAnd(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, 
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric) {
            this.rewardFunctionA = rewardFunctionA;
            this.rewardFunctionB = rewardFunctionB;
            this.entity_a = entity_a;
            this.entity_b = entity_b;
            this.distanceMetric = distanceMetric;
        }

        public override void Reset() {
            rewardFunctionA.Reset();
            rewardFunctionB.Reset();
        }
        public override float CalculateReward() {
            return Math.Min(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
        }
    }

    public class RewardFunctionOr : RewardFunction{
        // TODO: works in the assumption that A and B has the same reward
        public RewardFunction rewardFunctionA;
        public RewardFunction rewardFunctionB;

        public RewardFunctionOr(RewardFunction rewardFunctionA, RewardFunction rewardFunctionB, 
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric) {
            this.rewardFunctionA = rewardFunctionA;
            this.rewardFunctionB = rewardFunctionB;
            this.entity_a = entity_a;
            this.entity_b = entity_b;
            this.distanceMetric = distanceMetric;
        }

        public override void Reset() {
            rewardFunctionA.Reset();
            rewardFunctionB.Reset();
        }

        public override float CalculateReward() {
            return Math.Max(rewardFunctionA.CalculateReward(), rewardFunctionB.CalculateReward());
        }
    }


    public class RewardFunctionNot : RewardFunction{
        // TODO: works in the assumption that A is sparse
        public RewardFunction rewardFunctionA;

        public RewardFunctionNot(RewardFunction rewardFunctionA,
                GameObject entity_a, GameObject entity_b, IDistanceMetric distanceMetric) {
            this.rewardFunctionA = rewardFunctionA;
            this.entity_a = entity_a;
            this.entity_b = entity_b;
            this.distanceMetric = distanceMetric;
        }

        public override void Reset() {
            rewardFunctionA.Reset();
        }

        public override float CalculateReward() {
            if (rewardFunctionA.CalculateReward() > 0.0f) {
                return 0.0f;
            } else {
                return rewardFunctionA.rewardScalar;
            }
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