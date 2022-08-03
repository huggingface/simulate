using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class AgentManager : PluginBase {
        public static AgentManager instance { get; private set; }

        static Dictionary<string, Agent> agents;

        public AgentManager() {
            instance = this;
            agents = new Dictionary<string, Agent>();
        }

        // Find agent nodes
        public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
            foreach (Node node in Simulator.nodes.Values) {
                if (node.agentData != null)
                    agents.Add(node.name, new Agent(node));
            }
        }

        // Before simulator steps forward, execute agent actions
        public override void OnBeforeStep(EventData eventData) {
            if (eventData.inputKwargs.ContainsKey("action")) {
                try {
                    Dictionary<string, object> actions =
                        EventData.ParseKwarg<Dictionary<string, object>>(eventData.inputKwargs, "action");
                    foreach (string key in actions.Keys) {
                        if (!agents.TryGetValue(key, out Agent agent)) {
                            Debug.LogWarning($"Agent {key} not found");
                            continue;
                        }
                        agent.Step(actions[key]);
                    }
                } catch (System.Exception e) {
                    Debug.LogWarning("Failed to parse actions: " + e);
                }
            }
        }

        // After simulator steps forward, record agent reward and observations
        public override void OnStep(EventData eventData) {
            if (agents.Count == 0) return;
            Dictionary<string, Agent.Data> agentEventData = new Dictionary<string, Agent.Data>();
            foreach (string key in agents.Keys) {
                Agent agent = agents[key];
                Agent.Data data = agent.GetEventData();
                agentEventData.Add(key, data);
                agent.ZeroReward();
            }
            eventData.outputKwargs.Add("agents", agentEventData);
        }

        public override void OnReset() {
            foreach (Agent agent in agents.Values)
                agent.Reset();
        }

        public override void OnBeforeSceneUnloaded() {
            agents.Clear();
        }
    }
}