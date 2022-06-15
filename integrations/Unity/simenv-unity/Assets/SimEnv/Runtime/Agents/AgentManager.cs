using System;
using System.Collections.Generic;
using ISimEnv;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Agent Manager")]
    public class AgentManager : Singleton<AgentManager>, ISimulationManager {
        public event UnityAction onStep;

        List<Agent> _agents;
        public List<Agent> agents {
            get {
                _agents ??= new List<Agent>();
                return _agents;
            }
        }

        AgentWrapper _wrapper;
        public AgentWrapper agentsWrapper;

        public void Initialize() {
            // Hacky approach to connect agents to their cameras
            for(int i = 0; i < agents.Count; i++)
                agents[i].camera = RenderManager.instance.lookup[agents[i].node.GetComponentInChildren<Camera>()];

            SimulationManager.instance.Register(this);
        }

        public void Register(Agent agent) {
            Debug.Log(agent);
            if(!agents.Contains(agent))
                agents.Add(agent);
        }

        public void Step() {
            for(int i = 0; i < agents.Count; i++)
                agents[i].Step();
            onStep?.Invoke();
        }

        public void SetAction(List<float> action) {
            if(!Validate()) return;
            agents[0].SetAction(action);
        }

        public void GetObservation(UnityAction<IAgentObservation> callback) {
            if(!Validate()) {
                callback(default(IAgentObservation));
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