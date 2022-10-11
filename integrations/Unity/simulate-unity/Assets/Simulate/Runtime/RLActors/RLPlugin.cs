using System;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace Simulate.RlAgents {
    public class RLPlugin : PluginBase {
        public static RLPlugin instance { get; private set; }
        public static Dictionary<string, Actor> actors { get; private set; }
        public static Dictionary<string, ISensor> sensors { get; private set; }
        static List<Map> activeMaps;
        static List<Vector3> positions;
        static MapPool mapPool;
        static int poolSize;
        static int maxActorsPerMap = 0;
        static Dictionary<string, Buffer> sensorBuffers;
        static Buffer doneBuffer;
        static Buffer rewardBuffer;
        static bool active;

        public RLPlugin() {
            instance = this;
            actors = new Dictionary<string, Actor>();
            sensors = new Dictionary<string, ISensor>();
            mapPool = new MapPool();
            activeMaps = new List<Map>();
            positions = new List<Vector3>();
            sensorBuffers = new Dictionary<string, Buffer>();
            active = false;
        }

        public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
            // Find and cache sensor nodes
            foreach (Node node in Simulator.nodes.Values) {
                if (node.stateSensorData != null) {
                    sensors.Add(node.name, new StateSensor(node, node.stateSensorData));
                }
                if (node.raycastSensorData != null) {
                    sensors.Add(node.name, new RaycastSensor(node, node.raycastSensorData));
                }
            }
            // Find and cache actor nodes
            foreach (Node node in Simulator.nodes.Values) {
                if (node.isActor == true) {
                    actors.Add(node.name, new Actor(node));
                }
            }

            if (kwargs.TryParse<List<string>>("maps", out List<string> maps)) {
                Debug.Log("\"maps\" kwarg found, enabling map pooling");
                poolSize = 1;
                if (!kwargs.TryParse<int>("n_show", out poolSize))
                    Debug.LogWarning("Keyword \"n_show\" not provided, defaulting to 1");
                InitializeMapPool(maps);
            } else if (actors.Count > 0) {
                Debug.Log("Found agents but no maps provided. Defaulting to root as single map.");
                poolSize = 1;
                maps = new List<string> { Simulator.root.name };
                InitializeMapPool(maps);
            }

            active = actors.Count > 0;

            if (active)
                InitializeBuffers();
        }

        static void InitializeBuffers() {
            int nActiveMaps = activeMaps.Count;
            int nActors = maxActorsPerMap;
            // get the names and shapes of all the sensors, we assume all agents have the same sensors (for now)
            foreach (var sensor in activeMaps[0].actors.Values.First<Actor>().sensors) {
                List<int> bufferShape = new List<int>();
                bufferShape.Add(nActiveMaps);
                bufferShape.Add(nActors);
                bufferShape.AddRange(sensor.GetShape());
                Buffer sensorBuffer = new Buffer(
                    nActiveMaps * nActors * sensor.GetSize(),
                    bufferShape.ToArray(),
                    sensor.GetSensorBufferType()
                );
                // TODO: error is thrown due to multiple sensors with the same name here
                sensorBuffers.Add(sensor.GetName(), sensorBuffer);
            }
            int[] shape = { nActiveMaps, nActors, 1 };
            doneBuffer = new Buffer(nActiveMaps * nActors, shape, "float"); // we send bools as floats for now
            rewardBuffer = new Buffer(nActiveMaps * nActors, shape, "float");
        }

        static void InitializeMapPool(List<string> names) {
            foreach (string name in names) {
                if (!Simulator.nodes.TryGetValue(name, out Node root)) {
                    Debug.LogWarning($"Map root {name} not found");
                    continue;
                }
                Map map = new Map(root);
                maxActorsPerMap = Math.Max(map.actors.Count, maxActorsPerMap);
                mapPool.Push(map);
            }
            CreatePositionPool();
            PopulateMapPool();
        }

        static void PopulateMapPool() {
            for (int i = 0; i < poolSize; i++) {
                Map map = mapPool.Request();
                map.Reset(positions[i]);
                activeMaps.Add(map);
            }
        }

        // Before Simulator step, set up agent actions
        // Action is a:
        // A Dict (maps index) of Dict (agents names) to individual actions
        // Where "individual actions" is a list of integers/floats coresponding to the actions
        public override void OnBeforeStep(EventData eventData) {
            if (!active) return;
            if (eventData.inputKwargs.TryParse<Dictionary<string, List<List<List<float>>>>>("action", out Dictionary<string, List<List<List<float>>>> actions)) {
                for (int i = 0; i < activeMaps.Count; i++) {
                    // Create a dictionary of actions for the map
                    Dictionary<string, List<List<float>>> actionsForMap = new Dictionary<string, List<List<float>>>();
                    foreach (KeyValuePair<string, List<List<List<float>>>> action in actions) {
                        actionsForMap[action.Key] = action.Value[i];
                    }
                    activeMaps[i].SetActions(actionsForMap);
                }
            }
        }

        // After Simulator step, before rendering, check if any maps are done
        // If so, reset them, and update the map data
        public override void OnStep(EventData eventData) {
            if (!active) return;
            for (int i = 0; i < activeMaps.Count; i++) {
                List<(float reward, bool done)> rewardDones = activeMaps[i].GetActorRewardDones();
                bool done = false;
                int count = 0;
                foreach (var rewardDone in rewardDones) {
                    done = done || rewardDone.done;
                    doneBuffer.floatBuffer[i * maxActorsPerMap + count] = Convert.ToSingle(rewardDone.done);
                    rewardBuffer.floatBuffer[i * maxActorsPerMap + count] = rewardDone.reward;
                    count++;
                }
                // TODO: (Ed), should we reset when only one agent is done in a multiagent setting?
                if (done) ResetAt(i);
            }

            eventData.outputKwargs.Add("actor_done_buffer", doneBuffer);
            eventData.outputKwargs.Add("actor_reward_buffer", rewardBuffer);

            for (int i = 0; i < activeMaps.Count; i++)
                activeMaps[i].EnableActorSensors();
        }

        // After Simulator step, record sensor observations
        public override void OnAfterStep(EventData eventData) {
            if (!active) return;
            for (int i = 0; i < activeMaps.Count; i++) {
                activeMaps[i].GetActorObservations(sensorBuffers, i);
            }
            eventData.outputKwargs.Add("actor_sensor_buffers", sensorBuffers);
            for (int i = 0; i < activeMaps.Count; i++)
                activeMaps[i].DisableActorSensors();
        }

        static void ResetAt(int index) {
            Map map = activeMaps[index];
            mapPool.Push(map);

            map = mapPool.Request();
            map.SetActive(true);
            map.Reset(positions[index]);
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
            actors.Clear();
            mapPool.Clear();
            activeMaps.Clear();
            positions.Clear();
            sensorBuffers.Clear();
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