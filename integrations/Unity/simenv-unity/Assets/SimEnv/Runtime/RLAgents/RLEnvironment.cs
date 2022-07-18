using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class RLEnvironment {
        public Environment environment;

        private List<Agent> agents;

        public RLEnvironment(Environment environment) {
            agents = new List<Agent>();
            this.environment = environment;

            // Find all the agents that are children of the map root
            List<GameObject> gameObjects = GameObject.FindGameObjectsWithTag("Agent")
                .Where(g => g.transform.IsChildOf(environment.root.transform)).ToList();
            foreach (var obj in gameObjects) {
                var node = obj.GetComponent<Node>();
                Agent agent = new Agent(node, node.agentData);
                agents.Add(agent);
                agent.Initialize();
            }
            if(agents.Count == 0)
                Debug.LogWarning("RLAgents environment requires at least 1 agent.");
            Disable();
        }

        public void Step(List<float> actions, float frameRate) {
            // step the agents in this environment
            // TODO: extend for multi-agent setting
            agents[0].SetAction(actions);
            agents[0].AgentUpdate(frameRate);
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
            return agents[0].GetObservationShape();
        }

        public int GetObservationSize() {
            return agents[0].GetObservationSizes();
        }

        public void Reset() {
            agents[0].Reset();
        }

        public IEnumerator GetObservationCoroutine(uint[] pixelValues, int startingIndex) {
            yield return agents[0].GetObservationCoroutine(pixelValues, startingIndex);
        }

        public void SetPosition(Vector3 position) {
            environment.root.transform.position = position;
        }

        public void Enable() {
            environment.root.SetActive(true);
        }

        public void Disable() {
            environment.root.SetActive(false);
        }
    }
}