using UnityEngine;

namespace SimEnv {
    public class Node : MonoBehaviour {
        public ISensor sensor;
        public object referenceObject; // used to get a reference to Agent Class that controls this node

        public void Initialize() {
            Simulator.Register(this);
        }
    }
}