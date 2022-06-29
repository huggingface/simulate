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

        int obsSize;
        uint[] agentPixelValues;
        int frameSkip;
        float physicsUpdateRate;
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
            Agent exampleAgent = agents[0] as Agent;
            obsSize = exampleAgent.cam.camera.pixelWidth * exampleAgent.cam.camera.pixelHeight * 3;
            agentPixelValues = new uint[agents.Count * obsSize];

          
            frameSkip = Client.instance.frameSkip;
            physicsUpdateRate = Client.instance.physicsUpdateRate;
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
            for (int j = 0; j < frameSkip; j++) {
                if (agents != null) {
                    for (int i = 0; i < agents.Count; i++) {
                        Agent agent = agents[i] as Agent;
                        agent.AgentUpdate(physicsUpdateRate);
                    }
                } else {
                    Debug.LogWarning("Attempting to step environment without an Agent");
                }
                Simulator.Step(1, physicsUpdateRate);
                // Reward has to be updated after the simulate start as it is the result of the action the agent just took.
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
            List<Coroutine> coroutines = new List<Coroutine>();
            for (int i = 0; i < agents.Count; i++) {
                Agent agent = agents[i] as Agent;
                Coroutine coroutine = agent.GetObservationCoroutine(agentPixelValues, i * obsSize).RunCoroutine();
                coroutines.Add(coroutine);
            }

            foreach (var coroutine in coroutines) {
                yield return coroutine;
            }


            string string_array = JsonHelper.ToJson(agentPixelValues);
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
                Debug.LogWarning("Attempting to get a done without an Agent");
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