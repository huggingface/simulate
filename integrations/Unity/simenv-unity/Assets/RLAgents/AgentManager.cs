using System;
using System.Collections.Generic;
using System.Linq;
using ISimEnv;
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

        ISimulator simulator;

        public AgentManager(ISimulator simulator) {
            instance = this;
            this.simulator = simulator;
        }

        public void Initialize() {
            IEnumerable<ICamera> cameras = simulator.GetCameras();
            for(int i = 0; i < agents.Count; i++) {
                Camera agentCamera = agents[i].node.gameObject.GetComponentInChildren<Camera>();
                agents[i].renderCamera = cameras.FirstOrDefault(x => x.camera == agentCamera);
            }
        }

        public void Register(Agent agent) {
            if(!agents.Contains(agent))
                agents.Add(agent);
        }

        public void Step() {
            if(!Validate()) return;
            for(int i = 0; i < FRAME_SKIP; i++) {
                simulator.Step(1, FRAME_RATE);
                agents[0].Step();
            }
        }

        public void SetAction(List<float> action) {
            if(!Validate()) return;
            agents[0].SetAction(action);
        }

        public void GetObservation(UnityAction<CameraObservation> callback) {
            if(!Validate()) {
                callback(default(CameraObservation));
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