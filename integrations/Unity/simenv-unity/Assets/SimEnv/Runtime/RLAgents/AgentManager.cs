using System;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace SimEnv.RlAgents {
    public class AgentManager : PluginBase {
        public static AgentManager instance { get; private set; }
        public static Dictionary<string, Agent> agents { get; private set; }

        static MapPool mapPool;
        static List<Map> activeMaps;
        static List<Vector3> positions;
        static int poolSize;

        public AgentManager() {
            instance = this;
            agents = new Dictionary<string, Agent>();
            mapPool = new MapPool();
            activeMaps = new List<Map>();
            positions = new List<Vector3>();
        }

        public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
            foreach (Node node in Simulator.nodes.Values) {
                if (node.actionData != null)
                    agents.Add(node.name, new Agent(node));
            }
            if (kwargs.TryParse<List<string>>("maps", out List<string> maps)) {
                Debug.Log("\"maps\" kwarg found, enabling map pooling");
                poolSize = 1;
                if (!kwargs.TryParse<int>("n_show", out poolSize))
                    Debug.LogWarning("Keyword \"n_show\" not provided, defaulting to 1");
                InitializeMapPool(maps);
            } else if (agents.Count == 0) {
                Debug.LogWarning("Found agents but no maps provided. Pass a list of map root names with the \"maps\" kwarg");
            }
        }

        static void InitializeMapPool(List<string> names) {
            foreach (string name in names) {
                if (!Simulator.nodes.TryGetValue(name, out Node root)) {
                    Debug.LogWarning($"Map root {name} not found");
                    continue;
                }
                Map map = new Map(root);
                mapPool.Push(map);
            }
            CreatePositionPool();
            PopulateMapPool();
        }

        static void PopulateMapPool() {
            for (int i = 0; i < poolSize; i++) {
                Map map = mapPool.Request();
                map.SetPosition(positions[i]);
                activeMaps.Add(map);
            }
        }

        public override void OnBeforeStep(EventData eventData) {
            if (eventData.inputKwargs.TryParse<Dictionary<string, object>>("action", out Dictionary<string, object> actions)) {
                for (int i = 0; i < activeMaps.Count; i++) {
                    activeMaps[i].SetActions(actions[i.ToString()]);
                }
            }

        }

        public override void OnStep(EventData eventData) {
            if (agents.Count == 0) return;
            Dictionary<string, Agent.Data> agentEventData = new Dictionary<string, Agent.Data>();

            // The following code aims to implement the following:
            // consider the case of a pool of size four with two active maps
            // in normal interaction the python step() call returns obs, reward, done, info
            // where obs = {"agent_0": agent_0_obs, "agent_1": agent_1_obs}
            // where done = {"agent_0": agent_0_done, "agent_1": agent_1_done}
            // where reward = {"agent_0": agent_0_reward, "agent_1": agent_1_reward}
            // these are converted to arrays / lists / tensors for the RL learning algorithm

            // however when agent_0's episode ends and the environment resets these are required to be as follows
            // obs = {"agent_2": agent_2_obs, "agent_1": agent_1_obs}
            // done = {"agent_2": agent_0_done, "agent_1": agent_1_done}
            // reward = {"agent_2": agent_0_reward, "agent_1": agent_1_reward}

            // this implementation is hacky, and is forced to be like this due to the use of named agents in both the 
            // Unity and python side

            for (int i = 0; i < activeMaps.Count; i++) {
                (Dictionary<string, Agent.Data> mapEventData, bool done) = activeMaps[i].Step();

                if (mapEventData == null) continue;
                if (done) {
                    ResetAt(i);
                    Dictionary<string, Agent.Data> newMapEventData = activeMaps[i].GetAgentEventData();
                    // now for the hacky part, there are two assumptions here: 
                    // 1. both maps have the same number of agents / keys
                    // 2. the ordering of the mapEventData keys is the same in both cases
                    // we copy accross the old values to the new eventData dictionary
                    string[] oldKeys = mapEventData.Keys.ToArray<string>();
                    string[] newKeys = newMapEventData.Keys.ToArray<string>();
                    for (int j = 0; j < newMapEventData.Count; j++) {
                        newMapEventData[newKeys[j]].done = mapEventData[oldKeys[j]].done;
                        newMapEventData[newKeys[j]].reward = mapEventData[oldKeys[j]].reward;
                    }
                    mapEventData = newMapEventData;


                }
                foreach (string key in mapEventData.Keys)
                    agentEventData.Add(key, mapEventData[key]);
            }
            eventData.outputKwargs.Add("agents", agentEventData);
        }

        static void ResetAt(int index) {
            Map map = activeMaps[index];
            mapPool.Push(map);

            map = mapPool.Request();
            map.SetPosition(positions[index]);
            map.SetActive(true);
            activeMaps[index] = map;
        }

        static void ResetAt(int index) {
            Map map = activeMaps[index];
            mapPool.Push(map);

            map = mapPool.Request();
            map.SetPosition(positions[index]);
            map.SetActive(true);
            activeMaps[index] = map;
        }

        public override void OnReset() {
            for (int i = activeMaps.Count - 1; i >= 0; i--) {
                Map map = activeMaps[i];
                activeMaps.RemoveAt(i);
                mapPool.Push(map);
            }
            PopulateMapPool();
        }

        public override void OnBeforeSceneUnloaded() {
            agents.Clear();
            mapPool.Clear();
            activeMaps.Clear();
            positions.Clear();
        }

        static void CreatePositionPool() {
            Bounds bounds = new Bounds(Vector3.zero, Vector3.zero);
            foreach (Map map in mapPool) {
                Bounds mapBounds = map.bounds;
                bounds.Encapsulate(mapBounds);
            }

            Vector3 step = bounds.extents * 2f + new Vector3(1f, 0f, 1f);
            int count = 0;
            int root = Convert.ToInt32(Math.Ceiling(Math.Sqrt(Convert.ToDouble(poolSize))));
            bool stop = false;
            for (int i = 0; i < root; i++) {
                if (stop) break;
                for (int j = 0; j < root; j++) {
                    if (stop) break;
                    positions.Add(new Vector3(Convert.ToSingle(i) * step.x, 0f, Convert.ToSingle(j) * step.z));

                    count++;
                    if (count == poolSize) {
                        stop = true;
                    }
                }
            }
            Debug.Assert(count == poolSize);

        }
    }
}