using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv.Agents {
    public class AgentManager {
        public static AgentManager instance;

        List<Agent> _agents;
        public List<Agent> agents {
            get {
                _agents ??= new List<Agent>();
                return _agents;
            }
        }

        readonly float FRAME_RATE = 30;
        readonly float FRAME_SKIP = 15;

        public AgentManager() {

        }

        public void Initialize() {
            for (int i = 0; i < agents.Count; i++) {
                Camera agentCamera = agents[i].node.gameObject.GetComponentInChildren<Camera>();
                if (!Simulator.Cameras.TryGetValue(agentCamera, out RenderCamera camera)) {
                    Debug.LogWarning("Couldn't find agent camera.");
                    return;
                }
                agents[i].cam = camera;
            }
        }

        public void Register(Agent agent) {
            if (!agents.Contains(agent))
                agents.Add(agent);
        }

        public void Step(List<List<float>> actions) {
            if (agents != null) {
                for (int i = 0; i < agents.Count; i++) {
                    Agent agent = agents[i] as Agent;
                    List<float> action = actions[i];
                    agent.SetAction(action);
                }
            } else {
                Debug.LogWarning("Attempting to step environment without an Agent");
            }
            for (int j = 0; j < FRAME_SKIP; j++) {
                if (agents != null) {
                    for (int i = 0; i < agents.Count; i++) {
                        Agent agent = agents[i] as Agent;
                        agent.AgentUpdate();
                    }
                } else {
                    Debug.LogWarning("Attempting to step environment without an Agent");
                }
                Simulator.Step(1, FRAME_RATE);
                // RewardFunction has to be updated after the simulate start as it is the result of the action the agent just took.
                if (agents != null) {
                    for (int i = 0; i < agents.Count; i++) {
                        Agent agent = agents[i] as Agent;
                        agent.UpdateReward();
                    }
                } else {
                    Debug.LogWarning("Attempting to step environment without an Agent");
                }
            }
        }

        public void GetObservation(UnityAction<string> callback) {
            GetObservationCoroutine(callback).RunCoroutine();
        }

        private IEnumerator GetObservationCoroutine(UnityAction<string> callback) {
            Agent exampleAgent = agents[0] as Agent;
            // the coroutine has to be started from a monobehavior or something like that

            int obsSize = exampleAgent.cam.camera.pixelWidth * exampleAgent.cam.camera.pixelHeight * 3;
            uint[] pixel_values = new uint[agents.Count * obsSize]; // make this a member variable somewhere


            List<Coroutine> coroutines = new List<Coroutine>();
            for (int i = 0; i < agents.Count; i++) {
                Agent agent = agents[i] as Agent;
                Coroutine coroutine = agent.GetObservationCoroutine(pixel_values, i * obsSize).RunCoroutine();
                coroutines.Add(coroutine);
            }

            foreach (var coroutine in coroutines) {
                yield return coroutine;
            }


            string string_array = JsonHelper.ToJson(pixel_values);
            callback(string_array);
        }

        public float[] GetReward() {
            List<float> rewards = new List<float>();
            if (agents != null) {
                // Calculate the agent's reward for the current timestep 
                for (int i = 0; i < agents.Count; i++) {
                    Agent agent = agents[i] as Agent;
                    rewards.Add(agent.GetReward());
                    agent.ZeroReward();
                }
            } else {
                Debug.LogWarning("Attempting to get a reward without an Agent");
            }
            return rewards.ToArray<float>();
        }

        public bool[] GetDone() {
            // Check if the agent is in a terminal state 
            // TODO: add option for auto reset
            List<bool> dones = new List<bool>();
            if (agents != null) {
                // Calculate the agent's reward for the current timestep 
                for (int i = 0; i < agents.Count; i++) {
                    Agent agent = agents[i] as Agent;
                    dones.Add(agent.IsDone());
                }
            } else {
                Debug.LogWarning("Attempting to get a reward without an Agent");
            }
            return dones.ToArray<bool>();
        }

        public void ResetAgents() {
            // Reset the Agent & the environment # 
            // TODO add the environment reset, changing maps, etc!

            if (agents != null) {
                // Calculate the agent's reward for the current timestep 
                for (int i = 0; i < agents.Count; i++) {
                    Agent agent = agents[i] as Agent;
                    agent.Reset();
                }
            } else {
                Debug.LogWarning("Attempting to reset without an Agent");
            }
        }
    }
}