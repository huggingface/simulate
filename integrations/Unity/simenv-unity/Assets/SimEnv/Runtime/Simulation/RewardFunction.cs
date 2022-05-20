using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
namespace SimEnv {
    public interface IDistanceMetric {
        public float Calulate(GameObject e1, GameObject e2);
    }

    public class EuclideanDistance : IDistanceMetric {
        public float Calulate(GameObject e1, GameObject e2) {
            return Vector3.Distance(e1.transform.position, e2.transform.position);

        }
    }
    public class CosineDistance : IDistanceMetric {
        public float Calulate(GameObject e1, GameObject e2) {
            // TODO
            return Vector3.Distance(e1.transform.position, e2.transform.position);

        }
    }
    public abstract class RewardFunction {
        protected GameObject entity1;
        protected GameObject entity2;
        protected float rewardScalar = 1.0f;
        protected IDistanceMetric distanceMetric;
        public abstract void Reset();
        public abstract float CalculateReward();

    }

    public class DenseRewardFunction : RewardFunction {
        float bestDistance = float.PositiveInfinity;

        public override void Reset() {
            bestDistance = distanceMetric.Calulate(entity1, entity2);
            Debug.Log("reseting dense reward");
        }
        public DenseRewardFunction(GameObject entity1, GameObject entity2, IDistanceMetric distanceMetric) {
            this.entity1 = entity1;
            this.entity2 = entity2;
            this.distanceMetric = distanceMetric;
        }
        public override float CalculateReward() {
            float distance = distanceMetric.Calulate(entity1, entity2);

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
        float threshold = 1.0f;
        public SparseRewardFunction(GameObject entity1, GameObject entity2, IDistanceMetric distanceMetric, float threshold, bool isTerminal) {
            this.entity1 = entity1;
            this.entity2 = entity2;
            this.distanceMetric = distanceMetric;
            this.threshold = threshold;
            this.isTerminal = isTerminal;
        }
        public override void Reset() {
            hasTriggered = false;
            Debug.Log("reseting sparse reward");
        }

        public override float CalculateReward() {
            float reward = 0.0f;
            float distance = distanceMetric.Calulate(entity1, entity2);

            if (!hasTriggered && (distance < threshold)) {
                hasTriggered = true;
                reward += rewardScalar;
            }
            return reward * rewardScalar;
        }
    }
}