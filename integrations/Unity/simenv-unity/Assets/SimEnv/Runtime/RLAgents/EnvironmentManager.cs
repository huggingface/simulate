using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv.RlAgents {
    public class EnvironmentManager {
        public static EnvironmentManager instance;

        List<Environment> environmentPool = new List<Environment>();
        List<Environment> activeEnvironments = new List<Environment>();

        int nextEnvIndex = 0;

        float physicsUpdateRate = 1.0f / 30.0f;
        int frameSkip = 15;

        uint[] agentPixelValues;
        int obsSize;

        public void AddToPool(byte[] bytes) {
            GameObject map = GLTF.Importer.LoadFromBytes(bytes);
            Environment environment = new Environment(map);
            environmentPool.Add(environment);
        }

        public void ActivateEnvironments(int nEnvironments) {
            foreach (var env in environmentPool) {
                env.Disable();
            }

            Debug.Assert(nEnvironments <= environmentPool.Count);
            for (int i = 0; i < nEnvironments; i++) {
                Environment environment = GetNextEnv();
                environment.Enable();
                activeEnvironments.Add(environment);
            }

            obsSize = activeEnvironments[0].GetObservationSize();
            agentPixelValues = new uint[nEnvironments * obsSize];

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
            for (int i = 0; i < activeEnvironments.Count; i++) {
                activeEnvironments[i].Reset();
                activeEnvironments[i].Disable();
                activeEnvironments[i] = GetNextEnv();
                activeEnvironments[i].Enable();
            }
        }
        public void ResetAt(int i) {
            activeEnvironments[i].Reset();
            activeEnvironments[i].Disable();
            activeEnvironments[i] = GetNextEnv();
            activeEnvironments[i].Enable();
        }

        private Environment GetNextEnv() {
            Environment next = environmentPool[nextEnvIndex];
            nextEnvIndex++;
            nextEnvIndex %= environmentPool.Count;
            return next;
        }
        public float[] GetReward() {
            List<float> rewards = new List<float>();
            for (int i = 0; i < activeEnvironments.Count; i++) {
                rewards.Add(activeEnvironments[i].GetReward());
                activeEnvironments[i].ZeroReward();
            }
            return rewards.ToArray<float>();
        }

        public bool[] GetDone() {
            // Check if the agent is in a terminal state 
            // TODO: add option for auto reset
            List<bool> dones = new List<bool>();
            for (int i = 0; i < activeEnvironments.Count; i++) {
                dones.Add(activeEnvironments[i].GetDone());
            }
            return dones.ToArray<bool>();

        }

        public void GetObservation(UnityAction<string> callback) {
            // TODO: implement obs coroutine
            int[] obsShape = activeEnvironments[0].GetObservationShape();
            int[] shapeWithAgents = new int[obsShape.Length + 1];
            shapeWithAgents[0] = activeEnvironments.Count;                                // set the prepended value
            Array.Copy(obsShape, 0, shapeWithAgents, 1, obsShape.Length); // copy the old values
            string string_array = JsonHelper.ToJson(agentPixelValues, shapeWithAgents);
            callback(string_array);
        }

    }

}