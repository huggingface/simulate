using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using UnityEngine;


namespace SimEnv.RlAgents {

    public class EntityCache {
        private GameObject entity;
        private Vector3 entityOriginalPosition;
        public Quaternion entityOriginalRotation;
        public EntityCache(GameObject entity) {
            this.entity = entity;
            entityOriginalPosition = entity.transform.position;
            entityOriginalRotation = entity.transform.rotation;
        }
        public void Reset() {
            entity.transform.position = entityOriginalPosition;
            entity.transform.rotation = entityOriginalRotation;
        }

    }
    public class Environment {
        private List<Agent> agents;

        private List<EntityCache> decendants;
        private GameObject root;

        public Bounds bounds;

        public Environment(GameObject map) {
            root = map;
            agents = new List<Agent>();
            decendants = new List<EntityCache>();

            // Find all the agents that are children of the map root
            List<GameObject> gameObjects = new List<GameObject>(GameObject.FindGameObjectsWithTag("Agent")
            ).FindAll(g => g.transform.IsChildOf(map.transform));
            foreach (var obj in gameObjects) {
                var node = obj.GetComponent<Node>();
                Agent agent = node.referenceObject as Agent;
                agents.Add(agent);
                agent.Initialize();
            }
            bounds = GetLocalBoundsForObject(root);
            // back up all the child positions and rotations

            addChildrenToCache(map);
            Disable();
        }

        private void addChildrenToCache(GameObject gameObject) {
            foreach (Transform child in gameObject.transform) {
                EntityCache entityCache = new EntityCache(child.gameObject);
                decendants.Add(entityCache);
                addChildrenToCache(child.gameObject);
            }
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
        public void SetPosition(Vector3 position) {
            root.transform.position = position;
        }

        public void Step(List<float> actions, float physicsUpdateRate) {
            // step the agents in this environment
            // TODO: extend for multi-agent setting
            agents[0].SetAction(actions);
            agents[0].AgentUpdate(physicsUpdateRate);


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
        public List<int[]> GetObservationShapes() {
            return agents[0].GetObservationShapes();
        }
        public List<int> GetObservationSizes() {
            return agents[0].GetObservationSizes();
        }
        public List<string> GetSensorNames() {
            return agents[0].GetSensorNames();
        }
        public List<string> GetSensorTypes() {
            return agents[0].GetSensorTypes();
        }

        public void Reset() {
            foreach (EntityCache entityCache in decendants) {
                entityCache.Reset();
            }
            agents[0].Reset();
        }

        public void Disable() {
            root.SetActive(false);
        }
        public void Enable() {
            root.SetActive(true);
        }

        public IEnumerator GetObservationCoroutine(List<SensorBuffer> buffers, List<int> sizes, int index) {
            yield return agents[0].GetObservationCoroutine(buffers, sizes, index);
        }


    }
}