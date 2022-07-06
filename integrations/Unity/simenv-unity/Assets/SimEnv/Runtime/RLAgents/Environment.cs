using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using UnityEngine;


namespace SimEnv.RlAgents {
    public class Environment {
        private List<Agent> agents;
        private GameObject root;

        public Environment(GameObject map) {
            root = map;
            agents = new List<Agent>();

            // Find all the agents that are children of the map root
            List<GameObject> gameObjects = new List<GameObject>(GameObject.FindGameObjectsWithTag("Agent")
            ).FindAll(g => g.transform.IsChildOf(map.transform));
            foreach (var obj in gameObjects) {
                var node = obj.GetComponent<Node>();
                Agent agent = node.referenceObject as Agent;
                agents.Add(agent);
            }
        }

        public void Initialize() {
            for (int i = 0; i < agents.Count; i++) {
                agents[i].Initialize();
            }
        }

        public void Step(List<float> actions, float physicsUpdateRate) {
            // step the agents in this environment
            // TODO: extend for multi-agent setting
            agents[0].SetAction(actions);
            agents[0].AgentUpdate(physicsUpdateRate);


        }
        public void UpdateReward() {
            agents[0].UpdateReward();
            // a post step method for all
        }
        public float GetReward() {
            return agents[0].GetReward();
        }

        public void ZeroReward() {
            agents[0].ZeroReward();
        }
        public bool GetDone() {
            return agents[0].IsDone();
        }
        public int[] GetObservationShape() {
            return agents[0].getObservationShape();
        }
        public int GetObservationSize() {
            return agents[0].getObservationSizes();
        }

        public void Reset() {
            agents[0].Reset();
        }

        public void Disable() {
            root.SetActive(false);
        }
        public void Enable() {
            root.SetActive(true);
        }

        public IEnumerator GetObservationCoroutine(uint[] pixelValues, int startingIndex) {
            yield return agents[0].GetObservationCoroutine(pixelValues, startingIndex);
        }


    }
}