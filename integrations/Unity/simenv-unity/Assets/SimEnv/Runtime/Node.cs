using UnityEngine;

namespace SimEnv {
    public class Node : MonoBehaviour {
        public RenderCamera renderCamera;

        public void Initialize() {
            Simulator.Register(this);
        }
    }
}