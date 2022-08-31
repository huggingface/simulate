using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class Map {
        public Bounds bounds { get; private set; }
        public bool active { get; private set; }

        Node root;
        Dictionary<string, Agent> agents;

        public Map(Node root) {
            this.root = root;
            bounds = GetLocalBoundsForObject(root.gameObject);
            agents = new Dictionary<string, Agent>();
            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                if (AgentManager.agents.TryGetValue(node.name, out Agent agent))
                    agents.Add(node.name, agent);
            }


            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                if (node.rewardFunctionData != null) {
                    Debug.Log("found reward function in child" + node.rewardFunctionData.type);
                }
            }

        }

        public void SetActive(bool active) {
            root.gameObject.SetActive(active);
            this.active = active;
        }

        public void SetPosition(Vector3 position) {
            root.gameObject.transform.position = position;
        }

        public void SetActions(object action) {
            foreach (string key in agents.Keys)
                agents[key].Step(action);
        }

        public (Dictionary<string, Agent.Data>, bool) Step() {
            Dictionary<string, Agent.Data> agentEventData = new Dictionary<string, Agent.Data>();
            bool done = false;
            foreach (string key in agents.Keys) {
                Agent agent = agents[key];
                Agent.Data data = agent.GetEventData();
                done = done || data.done; // TODO: this assumes when one agent in the map is done the map should be reset
                agentEventData.Add(key, data);
                agent.ZeroReward();
            }
            return (agentEventData, done);
        }
        public Dictionary<string, Agent.Data> GetAgentEventData() {
            Dictionary<string, Agent.Data> agentEventData = new Dictionary<string, Agent.Data>();
            foreach (string key in agents.Keys) {
                Agent agent = agents[key];
                Agent.Data data = agent.GetEventData();
                agentEventData.Add(key, data);
            }
            return agentEventData;
        }

        public void Reset() {
            // TODO: Reset initial positions
            foreach (Agent agent in agents.Values)
                agent.Reset();
        }

        static Bounds GetLocalBoundsForObject(GameObject go) {
            var referenceTransform = go.transform;
            var b = new Bounds(Vector3.zero, Vector3.zero);
            RecurseEncapsulate(referenceTransform, ref b);
            return b;

            void RecurseEncapsulate(Transform child, ref Bounds bounds) {
                var mesh = child.GetComponent<MeshFilter>();
                if (mesh) {
                    var lsBounds = mesh.sharedMesh.bounds;
                    var wsMin = child.TransformPoint(lsBounds.center - lsBounds.extents);
                    var wsMax = child.TransformPoint(lsBounds.center + lsBounds.extents);
                    bounds.Encapsulate(referenceTransform.InverseTransformPoint(wsMin));
                    bounds.Encapsulate(referenceTransform.InverseTransformPoint(wsMax));
                }
                foreach (Transform grandChild in child.transform) {
                    RecurseEncapsulate(grandChild, ref bounds);
                }
            }
        }
    }
}
