using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace SimEnv.RlAgents {
    public class ActorManager : PluginBase {
        public static ActorManager instance { get; private set; }
        public static Dictionary<string, Actor> actors { get; private set; }

        static Dictionary<string, Actor.Data> currentActorEventData;
        static List<Map> activeMaps;
        static List<Vector3> positions;
        static MapPool mapPool;
        static int poolSize;
        static int maxActorsPerMap = 0;
        static Dictionary<string, Buffer> sensorBuffers;
        static Buffer doneBuffer;
        static Buffer rewardBuffer;

        public ActorManager() {
            instance = this;
            actors = new Dictionary<string, Actor>();
            currentActorEventData = new Dictionary<string, Actor.Data>();
            mapPool = new MapPool();
            activeMaps = new List<Map>();
            positions = new List<Vector3>();
            sensorBuffers = new Dictionary<string, Buffer>();
        }

        public override void OnSceneInitialized(Dictionary<string, object> kwargs) {
            foreach (Node node in Simulator.nodes.Values) {
                if (node.actionData != null) {
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

            InitializeBuffers();

        }
        static void InitializeBuffers() {

            Debug.Log("intializing buffers");
            // Creates buffers that hold the sensor measurements for all Actors
            // find the number of maps
            int nActiveMaps = activeMaps.Count;
            // find the maximum number of agents
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
                sensorBuffers.Add(sensor.GetName(), sensorBuffer);
            }
            int[] shape = { nActiveMaps, nActors, 1 };
            doneBuffer = new Buffer(nActiveMaps * nActors, shape, "float"); // we send bools as floats for now
            Debug.Log("intializing buffers done buffer");
            rewardBuffer = new Buffer(nActiveMaps * nActors, shape, "float");
            Debug.Log("intializing buffers reward buffer");


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
                map.SetPosition(positions[i]);
                activeMaps.Add(map);
            }
        }

        // Before Simulator step, set up agent actions
        public override void OnBeforeStep(EventData eventData) {
            if (eventData.inputKwargs.TryParse<Dictionary<string, object>>("action", out Dictionary<string, object> actions)) {
                for (int i = 0; i < activeMaps.Count; i++) {
                    activeMaps[i].SetActions(actions[i.ToString()]);
                }
            }
        }

        // After Simulator step, before rendering, check if any maps are done
        // If so, reset them, and update the map data
        public override void OnEarlyStep(EventData eventData) {
            currentActorEventData.Clear();
            for (int i = 0; i < activeMaps.Count; i++) {
                Dictionary<string, Actor.Data> mapData = activeMaps[i].GetActorEventData();
                bool done = false;
                int count = 0;
                foreach (Actor.Data data in mapData.Values) {
                    done = done || data.done;
                    doneBuffer.floatBuffer[i * maxActorsPerMap + count] = Convert.ToSingle(data.done);
                    rewardBuffer.floatBuffer[i * maxActorsPerMap + count] = data.reward;
                    count++;
                }


                if (done) { // TODO: (Ed), should we reset when only one agent is done in a multiagent setting?
                    ResetAt(i);
                    Dictionary<string, Actor.Data> newMapData = activeMaps[i].GetActorEventData();
                    string[] oldKeys = mapData.Keys.ToArray<string>();
                    string[] newKeys = newMapData.Keys.ToArray<string>();
                    for (int j = 0; j < mapData.Count; j++) {
                        newMapData[newKeys[j]].done = mapData[oldKeys[j]].done;
                        newMapData[newKeys[j]].reward = mapData[oldKeys[j]].reward;
                    }
                    mapData = newMapData;
                }
                foreach (string key in mapData.Keys)
                    currentActorEventData.Add(key, mapData[key]);
            }

            eventData.outputKwargs.Add("actor_done_buffer", doneBuffer);
            eventData.outputKwargs.Add("actor_reward_buffer", rewardBuffer);

            for (int i = 0; i < activeMaps.Count; i++)
                activeMaps[i].EnableActorSensors();
        }

        // After Simulator step, record sensor observations
        public override void OnStep(EventData eventData) {
            for (int i = 0; i < activeMaps.Count; i++) {
                activeMaps[i].GetActorObservations(currentActorEventData, sensorBuffers, i);
            }
            eventData.outputKwargs.Add("actors", currentActorEventData);
            eventData.outputKwargs.Add("actor_sensor_buffers", sensorBuffers);
            for (int i = 0; i < activeMaps.Count; i++)
                activeMaps[i].DisableActorSensors();
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
            actors.Clear();
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