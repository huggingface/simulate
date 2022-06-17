using UnityEngine;

namespace SimEnv.Agents {
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
        public GameObject entity1;
        public GameObject entity2;
        public float rewardScalar = 1.0f;
        public IDistanceMetric distanceMetric;
        public abstract void Reset();
        public abstract float CalculateReward();

    }

    public class DenseRewardFunction : RewardFunction {
        float bestDistance = float.PositiveInfinity;

        public override void Reset() {
            bestDistance = distanceMetric.Calculate(entity1, entity2);
        }
        public DenseRewardFunction(GameObject entity1, GameObject entity2, IDistanceMetric distanceMetric, float rewardScalar) {
            this.entity1 = entity1;
            this.entity2 = entity2;
            this.distanceMetric = distanceMetric;
            this.rewardScalar = rewardScalar;
        }
        public override float CalculateReward() {
            float distance = distanceMetric.Calculate(entity1, entity2);

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
        public SparseRewardFunction(GameObject entity1, GameObject entity2, IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal) {
            this.entity1 = entity1;
            this.entity2 = entity2;
            this.distanceMetric = distanceMetric;
            this.threshold = threshold;
            this.isTerminal = isTerminal;
            this.rewardScalar = rewardScalar;
        }
        public override void Reset() {
            hasTriggered = false;
        }

        public override float CalculateReward() {
            float reward = 0.0f;
            float distance = distanceMetric.Calculate(entity1, entity2);
            if (!hasTriggered && (distance < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
            }
            return reward * rewardScalar;
        }
    }


    public class TimeoutRewardFunction : SparseRewardFunction {
        int steps = 0;

        public TimeoutRewardFunction(GameObject entity1, GameObject entity2, IDistanceMetric distanceMetric, float rewardScalar, float threshold, bool isTerminal) :
                base(entity1, entity2, distanceMetric, rewardScalar, threshold, isTerminal) { }
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