using UnityEngine;

namespace SimEnv {
    public class Node : MonoBehaviour {
        public RenderCamera? camera = null;  // TODO We would like this more general than just Cameras

        public void Initialize() {
            Simulator.Register(this);
        }
    }
}