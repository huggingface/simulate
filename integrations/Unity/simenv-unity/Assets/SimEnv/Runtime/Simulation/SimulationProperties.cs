using UnityEngine;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Simulation Properties")]
    public class SimulationProperties : ScriptableObject {
        public int frameRate = 30;
        public int frameSkip = 4;
        
        public float frameInterval => 1f / frameRate;
    }
}