using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class Map {
        public Bounds bounds { get; private set; }
        public bool active { get; private set; }

        Node root;
        Dictionary<string, Actor> actors;
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

        public Dictionary<string, Actor.Data> GetActorEventData() {
            Dictionary<string, Actor.Data> actorEventData = new Dictionary<string, Actor.Data>();
            foreach (string key in actors.Keys) {
                Actor actor = actors[key];
                Actor.Data data = actor.GetEventData();
                actorEventData.Add(key, data);
            }
            return actorEventData;
        }

        public void GetActorObservations(Dictionary<string, Actor.Data> actorEventData) {
            foreach (string key in actors.Keys) {
                Actor actor = actors[key];
                actor.ReadSensorObservations(actorEventData[key]);
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
