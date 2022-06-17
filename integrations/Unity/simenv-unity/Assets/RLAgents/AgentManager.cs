using System;
using System.Collections.Generic;
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
            for(int i = 0; i < agents.Count; i++) {
                Camera agentCamera = agents[i].node.gameObject.GetComponentInChildren<Camera>();
                if(!Simulator.Cameras.TryGetValue(agentCamera, out RenderCamera camera)) {
                    Debug.LogWarning("Couldn't find agent camera.");
                    return;
                }
                agents[i].cam = camera;
            }
        }

        public void Register(Agent agent) {
            if(!agents.Contains(agent))
                agents.Add(agent);
        }

        public void Step() {
            if(!Validate()) return;
            for(int i = 0; i < FRAME_SKIP; i++) {
                Simulator.Step(1, FRAME_RATE);
                agents[0].AgentUpdate();
            }
        }

        public void SetAction(List<float> action) {
            if(!Validate()) return;
            agents[0].SetAction(action);
        }

        public void GetObservation(UnityAction<string> callback) {
            if(!Validate()) {
                callback("Error: No agent found");
                return;
            }
            agents[0].GetObservation(callback);
        }

        public float GetReward() {
            if(!Validate()) return 0;
            float reward = 0.0f;
            reward += agents[0].GetReward();
            agents[0].ZeroReward();
            return reward;
        }

        public bool GetDone() {
            if(!Validate()) return false;
            return agents[0].IsDone();
        }

        public void ResetAgents() {
            if(!Validate()) return;
            agents[0].Reset();
        }

        bool Validate() {
            if(agents.Count == 0) {
                Debug.LogWarning("No agent found");
                return false;
            }
            if(agents.Count > 1)
                throw new NotImplementedException("Multi agent not implemented");
            return true;
        }
    }
}