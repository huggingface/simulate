using ISimEnv;
using UnityEngine;

namespace SimEnv {
    public class Node : MonoBehaviour, INode {
        public void Initialize() {
            SimulationManager.instance.Register(this);
        }

        public void Release() {
            Destroy(gameObject);
        }
    }
}