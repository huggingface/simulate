using UnityEngine.Events;

namespace SimEnv {
    public interface ISimulationManager {
        event UnityAction onStep;
        void Step();
    }
}