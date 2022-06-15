using ISimEnv;
using UnityEngine;

namespace SimEnv {
    public class Node : MonoBehaviour, INode {
        public new string name => gameObject.name;
        public Vector3 position => transform.position;
        public Quaternion rotation => transform.rotation;

        public void Initialize() {
            SimulationManager.instance.Register(this);
        }

        public void Release() {
            Destroy(gameObject);
        }
    }
}