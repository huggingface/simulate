using UnityEngine;
using ISimEnv;
using System;
using System.Linq;
using System.Collections.Generic;

namespace SimEnv {
    public class SimObjectBase : MonoBehaviour, ISimObject {
        public GameObject GameObject => gameObject;
        public string Name => gameObject.name;

        List<ISimObjectExtension> extensions;

        public virtual void Initialize() {
            ISimulator.Register(this);
            extensions = Simulator.SimObjectExtensions
                .Select(x => Activator.CreateInstance(x))
                .Cast<ISimObjectExtension>().ToList();
            extensions.ForEach(x => x.OnCreated(this));
        }

        public virtual void Interact(params object[] args) {
            extensions.ForEach(x => x.OnInteract(args));
        }

        public virtual void Deinitialize() {
            extensions.ForEach(x => x.OnReleased());
            ISimulator.Unregister(this);
        }

        protected virtual void OnDestroy() {
            Deinitialize();
        }
    }
}
