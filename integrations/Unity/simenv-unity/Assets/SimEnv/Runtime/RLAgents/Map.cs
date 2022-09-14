using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class Map {
        public Bounds bounds { get; private set; }
        public bool active { get; private set; }

        Node root;
        public Dictionary<string, Actor> actors;
        List<Node> children;

        public Map(Node root) {
            this.root = root;
            bounds = GetLocalBoundsForObject(root.gameObject);
            actors = new Dictionary<string, Actor>();
            children = new List<Node>();
            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                if (ActorManager.actors.TryGetValue(node.name, out Actor Actor))
                    actors.Add(node.name, Actor);
                children.Add(node);
            }
            initMapSensors();
        }

        private void initMapSensors() {
            // finds sensors that are children of the map, but not of the actors (in this map)
            // these sensors are considered to be "global" sensors that are static relative to a particular
            // agent
            foreach (Node node2 in Simulator.nodes.Values) {
                if (node2.camera != null && node2.gameObject.transform.IsChildOf(root.gameObject.transform)) {
                    TryAddCameraToActors(node2);
                }
                // search children for StateSensors
                if (node2.sensor != null && node2.gameObject.transform.IsChildOf(root.gameObject.transform)) {
                    TryAddSensorToActors(node2);
                }
            }
        }

        private void TryAddCameraToActors(Node node) {
            foreach (var actor in actors.Values) {
                if (node.gameObject.transform.IsChildOf(actor.node.gameObject.transform)) {
                    return;
                }
            }
            CameraSensor cameraSensor = new CameraSensor(node.camera, node.cameraData.sensor_name); // same instance shared across actors
            foreach (var actor in actors.Values) {
                actor.sensors.Add(cameraSensor);
            }
        }
        private void TryAddSensorToActors(Node node) {
            foreach (var actor in actors.Values) {
                if (node.gameObject.transform.IsChildOf(actor.node.gameObject.transform)) {
                    return;
                }
            }
            foreach (var actor in actors.Values) {
                actor.sensors.Add(node.sensor);
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
            foreach (string key in actors.Keys)
                actors[key].SetAction(action);
        }

        public List<(float, bool)> GetActorRewardDones() {
            List<(float, bool)> rewardDones = new List<(float, bool)>();
            //Dictionary<string, Actor.Data> actorEventData = new Dictionary<string, Actor.Data>();

            foreach (string key in actors.Keys) {
                Actor actor = actors[key];
                var doneReward = actor.GetRewardDone();
                rewardDones.Add(doneReward);
            }
            return rewardDones;
        }

        public void GetActorObservations(Dictionary<string, Buffer> sensorBuffers, int mapIndex) {
            int actorIndex = 0;
            foreach (string key in actors.Keys) {
                Actor actor = actors[key];
                actor.ReadSensorObservations(sensorBuffers, mapIndex, actorIndex);
                actorIndex++;
            }
        }

        public void Reset() {
            foreach (Node node in children)
                node.ResetState();
            foreach (Actor actor in actors.Values)
                actor.Reset();
        }

        public void EnableActorSensors() {
            foreach (Actor Actor in actors.Values)
                Actor.EnableSensors();
        }

        public void DisableActorSensors() {
            foreach (Actor Actor in actors.Values)
                Actor.DisableSensors();
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
