using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using SimEnv;
using SimEnv.RlAgents;
public class TestRewardFunctions {
    // A Test behaves as an ordinary method
    [Test]
    public void TestRewardFunctionsSimplePasses() {
        // Use the Assert class to test conditions


        Node node1 = new Node();
        Node node2 = new Node();
        EuclideanDistance distance = new EuclideanDistance();

        DenseRewardFunction rewardFunction = new DenseRewardFunction(
            node1, node2, distance, 1.0f
        );


        float reward = rewardFunction.CalculateReward();

        Assert.AreEqual(reward, 0f);
    }

    // // A UnityTest behaves like a coroutine in Play Mode. In Edit Mode you can use
    // // `yield return null;` to skip a frame.
    // [UnityTest]
    // public IEnumerator TestRewardFunctionsWithEnumeratorPasses()
    // {
    //     // Use the Assert class to test conditions.
    //     // Use yield to skip a frame.
    //     yield return null;
    // }
}
