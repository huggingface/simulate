using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class EnvironmentManager {
        public static EnvironmentManager instance;

        Queue<Environment> environmentQueue = new Queue<Environment>();
        List<Vector3> positionPool = new List<Vector3>();
        List<Environment> activeEnvironments = new List<Environment>();

        int nextEnvIndex = 0;

        float physicsUpdateRate = 1.0f / 30.0f;
        int frameSkip = 4;

        uint[] agentPixelValues;
        int obsSize;

        public void AddToPool(byte[] bytes) {
            GameObject map = GLTF.Importer.LoadFromBytes(bytes);
            Environment environment = new Environment(map);
            environmentQueue.Enqueue(environment);

        }

        public void ActivateEnvironments(int nEnvironments) {
            CreatePositionPool(nEnvironments);
            if (nEnvironments == -1) {
                nEnvironments = environmentQueue.Count;
            }
            Debug.Assert(nEnvironments <= environmentQueue.Count);
            for (int i = 0; i < nEnvironments; i++) {
                Environment environment = environmentQueue.Dequeue();
                environment.SetPosition(positionPool[i]);
                environment.Enable();
                environment.Reset();
                activeEnvironments.Add(environment);
            }

            obsSize = activeEnvironments[0].GetObservationSize();
            agentPixelValues = new uint[nEnvironments * obsSize];
            frameSkip = Client.instance.frameSkip;
            physicsUpdateRate = Client.instance.physicsUpdateRate;
        }

        private void CreatePositionPool(int nEnvironments) {
            Bounds bounds = new Bounds(Vector3.zero, Vector3.zero);
            foreach (var env in environmentQueue) {
                Bounds envBounds = env.bounds;
                bounds.Encapsulate(envBounds);
            }

            Vector3 step = bounds.extents * 2f + new Vector3(1f, 0f, 1f);

            int count = 0;
            int root = Convert.ToInt32(Math.Ceiling(Math.Sqrt(Convert.ToDouble(nEnvironments))));
            bool stop = false;
            for (int i = 0; i < root; i++) {
                if (stop) break;
                for (int j = 0; j < root; j++) {
                    if (stop) break;
                    positionPool.Add(new Vector3(Convert.ToSingle(i) * step.x, 0f, Convert.ToSingle(j) * step.z));

                    count++;
                    if (count == nEnvironments) {
                        stop = true;
                    }
                }
            }
            Debug.Assert(count == nEnvironments);

        }

        public void Step(List<List<float>> actions) {
            for (int j = 0; j < frameSkip; j++) {
                for (int i = 0; i < activeEnvironments.Count; i++) {
                    activeEnvironments[i].Step(actions[i], physicsUpdateRate);
                }
                // sim calls the physics update
                Simulator.Step(1, physicsUpdateRate);
                // update rewards
                for (int i = 0; i < activeEnvironments.Count; i++) {
                    activeEnvironments[i].UpdateReward();
                }
            }
        }

        public void ResetAgents() {
            Debug.Log("resetting agents");
            for (int i = 0; i < activeEnvironments.Count; i++) {
                ResetAt(i);
            }
        }
        public void ResetAt(int i) {

            activeEnvironments[i].SetPosition(new Vector3(-10f, 0f, -10f));
            activeEnvironments[i].Disable();
            environmentQueue.Enqueue(activeEnvironments[i]);

            activeEnvironments[i] = environmentQueue.Dequeue();
            activeEnvironments[i].SetPosition(positionPool[i]);
            activeEnvironments[i].Enable();
            activeEnvironments[i].Reset();


        }
        public float[] GetReward() {
            List<float> rewards = new List<float>();
            for (int i = 0; i < activeEnvironments.Count; i++) {
                rewards.Add(activeEnvironments[i].GetReward());
                activeEnvironments[i].ZeroReward();
            }
            return rewards.ToArray<float>();
        }

        public bool[] GetDone(bool autoReset = true) {
            // Check if the agent is in a terminal state 
            // TODO: add option for auto reset
            List<bool> dones = new List<bool>();
            for (int i = 0; i < activeEnvironments.Count; i++) {
                bool done = activeEnvironments[i].GetDone();
                dones.Add(done);
                if (done && autoReset) {
                    ResetAt(i);
                }
            }
            return dones.ToArray<bool>();

        }

        public void GetObservation(UnityAction<string> callback) {
            GetObservationCoroutine(callback).RunCoroutine();
        }
        private IEnumerator GetObservationCoroutine(UnityAction<string> callback) {
            // TODO: implement obs coroutine
            int[] obsShape = activeEnvironments[0].GetObservationShape();
            int[] shapeWithAgents = new int[obsShape.Length + 1];
            shapeWithAgents[0] = activeEnvironments.Count;                                // set the prepended value
            Array.Copy(obsShape, 0, shapeWithAgents, 1, obsShape.Length); // copy the old values

            List<Coroutine> coroutines = new List<Coroutine>();
            for (int i = 0; i < activeEnvironments.Count; i++) {
                Coroutine coroutine = activeEnvironments[i].GetObservationCoroutine(agentPixelValues, i * obsSize).RunCoroutine();
                coroutines.Add(coroutine);
            }

            foreach (var coroutine in coroutines) {
                yield return coroutine;
            }

            string string_array = JsonHelper.ToJson(agentPixelValues, shapeWithAgents);
            callback(string_array);
        }

    }

}