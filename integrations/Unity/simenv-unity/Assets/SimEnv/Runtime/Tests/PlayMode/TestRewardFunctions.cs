using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using SimEnv;
using SimEnv.RlAgents;
public class TestRewardFunctions {
    // A Test behaves as an ordinary method
    [UnityTest]
    public IEnumerator TestDenseRewardFunction() {

        var entity1 = new GameObject();
        entity1.AddComponent<Node>();
        entity1.transform.position = Vector3.forward;

        var entity2 = new GameObject();
        entity2.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();

        DenseRewardFunction rewardFunction = new DenseRewardFunction(
            entity1.GetComponent<Node>(), entity2.GetComponent<Node>(), distance, 1.0f
        );

        rewardFunction.Reset();
        float reward = rewardFunction.CalculateReward();
        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);

        entity1.transform.position = Vector3.zero;

        Assert.AreEqual(rewardFunction.CalculateReward(), 1f);
        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);

        yield return null;
    }
}
