using System.Collections;
using UnityEngine.Events;

namespace ISimEnv {
    public interface IAgent {
        void GetObservation(UnityAction<IAgentObservation> callback);
    }
}