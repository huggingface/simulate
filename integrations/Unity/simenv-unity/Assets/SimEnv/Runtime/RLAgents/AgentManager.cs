using System;
using System.Collections.Generic;
using UnityEngine;

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
                if (node.agentData != null)
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
                foreach (Map map in activeMaps)
                    map.SetActions(actions);
            }
        }

        public override void OnStep(EventData eventData) {
            if (agents.Count == 0) return;
            Dictionary<string, Agent.Data> agentEventData = new Dictionary<string, Agent.Data>();
            Stack<Map> doneMaps = new Stack<Map>();
            foreach (Map map in activeMaps) {
                (Dictionary<string, Agent.Data> mapEventData, bool done) = map.Step();
                if (mapEventData != null) {
                    foreach (string key in mapEventData.Keys)
                        agentEventData.Add(key, mapEventData[key]);
                }
                if (done)
                    doneMaps.Push(map);
            }
            eventData.outputKwargs.Add("agents", agentEventData);
            while (doneMaps.Count > 0) {
                Map map = doneMaps.Pop();
                int index = activeMaps.IndexOf(map);
                ResetAt(index);
            }
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