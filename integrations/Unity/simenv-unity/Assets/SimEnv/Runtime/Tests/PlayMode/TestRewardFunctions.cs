using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Simulate;
using Simulate.RlAgents;
public class TestRewardFunctions {
    [UnityTest]
    public IEnumerator TestDenseRewardFunctionBestEuclidean() {
        // create two objects at 1 unit separation, ensure the move them together product the appropiate reward
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = Vector3.forward;

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        BestDistance distance = new BestDistance(new EuclideanDistance());

        DenseRewardFunction rewardFunction = new DenseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f
        );

        rewardFunction.Reset();
        float reward = rewardFunction.CalculateReward();
        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);

        entityA.transform.position = Vector3.zero;

        Assert.AreEqual(rewardFunction.CalculateReward(), 1f);
        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestDenseRewardFunctionEuclidean() {
        // create two objects at 1 unit separation, ensure the move them together product the appropiate reward
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = Vector3.forward;

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();

        DenseRewardFunction rewardFunction = new DenseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f
        );

        rewardFunction.Reset();
        float reward = rewardFunction.CalculateReward();
        Assert.AreEqual(rewardFunction.CalculateReward(), 1f);

        entityA.transform.position = Vector3.zero;

        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);
        entityA.transform.position = Vector3.forward;
        Assert.AreEqual(rewardFunction.CalculateReward(), 1f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestSparseRewardFunction() {
        // Places two objects at 10 units distance, move one to each other until the reward triggers once at 4.9 metres
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = new Vector3(10, 0, 0);

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();

        SparseRewardFunction rewardFunction = new SparseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f, 4.9f, false, false, true
        );

        rewardFunction.Reset();

        for (int i = 0; i < 5; i++) {
            entityA.transform.position -= new Vector3(1f, 0, 0);
            Assert.AreEqual(rewardFunction.CalculateReward(), 0f);
        }

        // trigger the reward
        entityA.transform.position -= new Vector3(1f, 0, 0);
        Assert.AreEqual(rewardFunction.CalculateReward(), 1f);
        // this should only be triggered once
        Assert.AreEqual(rewardFunction.CalculateReward(), 0f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestRewardFunctionAnd() {
        // Builds two reward functions and ensures the and reward functions correctly
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = new Vector3(1, 0, 0);

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();
        SparseRewardFunction rewardFunctionA = new SparseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        var entityC = new GameObject();
        entityC.AddComponent<Node>();
        entityC.transform.position = new Vector3(1, 0, 0);

        var entityD = new GameObject();
        entityD.AddComponent<Node>();

        SparseRewardFunction rewardFunction2B = new SparseRewardFunction(
            entityC.GetComponent<Node>(), entityD.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        RewardFunctionAnd rewardFunctionAnd = new RewardFunctionAnd(rewardFunctionA, rewardFunction2B, false);
        rewardFunctionAnd.Reset();

        Assert.AreEqual(rewardFunctionAnd.CalculateReward(), 0f);
        entityA.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionAnd.CalculateReward(), 0f);

        entityC.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionAnd.CalculateReward(), 1f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestRewardFunctionOr() {
        // Builds two reward functions and ensures the or reward functions correctly
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = new Vector3(1, 0, 0);

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();
        SparseRewardFunction rewardFunctionA = new SparseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        var entityC = new GameObject();
        entityC.AddComponent<Node>();
        entityC.transform.position = new Vector3(1, 0, 0);

        var entityD = new GameObject();
        entityD.AddComponent<Node>();

        SparseRewardFunction rewardFunction2B = new SparseRewardFunction(
            entityC.GetComponent<Node>(), entityD.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        RewardFunctionOr rewardFunctionOr = new RewardFunctionOr(rewardFunctionA, rewardFunction2B, false);
        rewardFunctionOr.Reset();

        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 0f);
        entityA.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 1f);

        entityA.transform.position = Vector3.forward;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 0f);

        entityC.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 1f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestRewardFunctionXor() {
        // Builds two reward functions and ensures the or reward functions correctly
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = new Vector3(1, 0, 0);

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();
        SparseRewardFunction rewardFunctionA = new SparseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        var entityC = new GameObject();
        entityC.AddComponent<Node>();
        entityC.transform.position = new Vector3(1, 0, 0);

        var entityD = new GameObject();
        entityD.AddComponent<Node>();

        SparseRewardFunction rewardFunction2B = new SparseRewardFunction(
            entityC.GetComponent<Node>(), entityD.GetComponent<Node>(), distance, 1.0f, 0.5f, false, false, false
        );

        RewardFunctionXor rewardFunctionOr = new RewardFunctionXor(rewardFunctionA, rewardFunction2B, false);
        rewardFunctionOr.Reset();

        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 0f);
        entityA.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 1f);

        entityA.transform.position = Vector3.forward;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 0f);

        entityC.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 1f);

        entityA.transform.position = Vector3.zero;
        Assert.AreEqual(rewardFunctionOr.CalculateReward(), 0f);

        yield return null;
    }


    [UnityTest]
    public IEnumerator TestRewardFunctionNot() {
        var entityA = new GameObject();
        entityA.AddComponent<Node>();
        entityA.transform.position = new Vector3(10, 0, 0);

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        EuclideanDistance distance = new EuclideanDistance();

        SparseRewardFunction rewardFunction = new SparseRewardFunction(
            entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), distance, 1.0f, 4.9f, false, false, true
        );

        RewardFunctionNot rewardFunctionNot = new RewardFunctionNot(rewardFunction, false);

        rewardFunctionNot.Reset();

        for (int i = 0; i < 5; i++) {
            entityA.transform.position -= new Vector3(1f, 0, 0);
            Assert.AreEqual(rewardFunctionNot.CalculateReward(), 1f);
        }

        // trigger the reward
        entityA.transform.position -= new Vector3(1f, 0, 0);
        Assert.AreEqual(rewardFunctionNot.CalculateReward(), 0f);
        // this should only be triggered once
        Assert.AreEqual(rewardFunctionNot.CalculateReward(), 1f);

        yield return null;
    }
    [UnityTest]
    public IEnumerator TestRewardFunctionSee() {
        var entityA = new GameObject();
        entityA.AddComponent<Node>();

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        SeeRewardFunction seeRewardFunction = new SeeRewardFunction(entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), null, 1.0f, 45, false, false, false);
        seeRewardFunction.Reset();

        for (int i = -180; i < 180; i++) {
            entityA.transform.position = new Vector3(Mathf.Sin(Mathf.Deg2Rad * (float)(i)), 0f, Mathf.Cos(Mathf.Deg2Rad * (float)(i)));
            if (i > -45 && i < 45) {
                Assert.AreEqual(seeRewardFunction.CalculateReward(), 1f);
            } else {
                Assert.AreEqual(seeRewardFunction.CalculateReward(), 0f);
            }
        }

        yield return null;
    }

    [UnityTest]
    public IEnumerator TestRewardFunctionAngleTo() {
        // Places two objects at 10 units distance, move one to each other until the reward triggers once at 4.9 metres

        var entityA = new GameObject();
        entityA.AddComponent<Node>();

        var entityB = new GameObject();
        entityB.AddComponent<Node>();

        AngleToRewardFunction angleToRewardFunction = new AngleToRewardFunction(entityA.GetComponent<Node>(), entityB.GetComponent<Node>(), null, 1f, Vector3.forward, 45f, false, false, false);

        angleToRewardFunction.Reset();

        for (int i = -180; i < 180; i++) {
            entityA.transform.position = new Vector3(Mathf.Sin(Mathf.Deg2Rad * (float)(i)), 0f, Mathf.Cos(Mathf.Deg2Rad * (float)(i)));
            //Debug.Log(i.ToString() + " " + angleToRewardFunction.CalculateReward().ToString() + " " + entityB.transform.position.ToString() + " " + entityA.GetComponent<Node>().transform.forward);
            if (i > -45 && i < 45) {
                Assert.AreEqual(angleToRewardFunction.CalculateReward(), 1f);
            } else {
                Assert.AreEqual(angleToRewardFunction.CalculateReward(), 0f);
            }
        }

        yield return null;
    }
}
