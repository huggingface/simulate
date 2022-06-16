using UnityEngine;
using ISimEnv;

namespace SimEnv {
    public class SimAgentBase : MonoBehaviour, ISimAgent {
        public GameObject GameObject => gameObject;
        public string Name => gameObject.name;

        public virtual void Initialize() {
            ISimulator.Register(this);
        }

        public virtual void Deinitialize() {
            ISimulator.Unregister(this);
        }

        protected virtual void OnDestroy() {
            Deinitialize();
        }
    }
}