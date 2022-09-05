using System.Collections.Generic;
using UnityEngine;

namespace SimEnv.RlAgents {
    public class EntityCache {
        private GameObject entity;
        private Rigidbody rigidbody;
        private Vector3 entityOriginalPosition;
        private Quaternion entityOriginalRotation;
        public EntityCache(GameObject entity) {
            this.entity = entity;
            entityOriginalPosition = entity.transform.localPosition;
            entityOriginalRotation = entity.transform.localRotation;
            rigidbody = entity.GetComponent<Rigidbody>();
        }
        public void Reset() {
            entity.transform.localPosition = entityOriginalPosition;
            entity.transform.localRotation = entityOriginalRotation;

            if (rigidbody != null) {
                rigidbody.velocity = Vector3.zero;
                rigidbody.angularVelocity = Vector3.zero;
            }

        }

    }
    public class Map {
        public Bounds bounds { get; private set; }
        public bool active { get; private set; }

        Node root;
        Dictionary<string, Actor> actors;
        private List<EntityCache> decendants;

        public Map(Node root) {
            this.root = root;
            decendants = new List<EntityCache>();
            bounds = GetLocalBoundsForObject(root.gameObject);
            actors = new Dictionary<string, Actor>();
            foreach (Node node in root.GetComponentsInChildren<Node>(true)) {
                if (ActorManager.actors.TryGetValue(node.name, out Actor Actor))
                    actors.Add(node.name, Actor);
            }
            addChildrenToCache(root.gameObject);

        }
        private void addChildrenToCache(GameObject gameObject) {
            foreach (Transform child in gameObject.transform) {
                EntityCache entityCache = new EntityCache(child.gameObject);
                decendants.Add(entityCache);
                addChildrenToCache(child.gameObject);
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
                actors[key].Step(action);
        }

        public (Dictionary<string, Actor.Data>, bool) Step() {
            Dictionary<string, Actor.Data> ActorEventData = new Dictionary<string, Actor.Data>();
            bool done = false;
            foreach (string key in actors.Keys) {
                Actor Actor = actors[key];
                Actor.Data data = Actor.GetEventData();
                done = done || data.done; // TODO: this assumes when one Actor in the map is done the map should be reset
                ActorEventData.Add(key, data);
                Actor.ZeroReward();
            }
            return (ActorEventData, done);
        }
        public Dictionary<string, Actor.Data> GetActorEventData() {
            Dictionary<string, Actor.Data> ActorEventData = new Dictionary<string, Actor.Data>();
            foreach (string key in actors.Keys) {
                Actor Actor = actors[key];
                Actor.Data data = Actor.GetEventData();
                ActorEventData.Add(key, data);
            }
            return ActorEventData;
        }

        public void Reset() {
            foreach (EntityCache entityCache in decendants) {
                entityCache.Reset();
            }
            foreach (Actor Actor in actors.Values)
                Actor.Reset();
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
