using System;
using System.Collections.Generic;
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

        public void Initialize() {
            // Hacky way to connect agent to its camera
            for(int i = 0; i < agents.Count; i++)
                agents[i].camera = RenderManager.instance.lookup[agents[i].node.GetComponentInChildren<Camera>()];
            SimulationManager.instance.Register(this);
        }

        public void Register(Agent agent) {
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

        public void GetObservation(UnityAction<Color32[]> callback) {
            if(!Validate()) {
                callback(new Color32[0]);
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
                Debug.LogWarning("No agent founds");
                return false;
            }
            if(agents.Count > 1)
                throw new NotImplementedException("Multi agent not implemented");
            return true;
        }
    }
}