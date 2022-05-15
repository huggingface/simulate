using UnityEngine;
using UnityEngine.Events;
using ISimEnv;

namespace SimEnv {
    public class SimObjectBase : MonoBehaviour, ISimObject {
        public virtual event UnityAction<ISimObject> OnDeinitialize;

        public GameObject GameObject => gameObject;
        public string Name => gameObject.name;

        public virtual void Initialize() {
            ISimulator.Register(this);
        }

        public virtual void Deinitialize() {
            OnDeinitialize?.Invoke(this);
        }
    }
}
