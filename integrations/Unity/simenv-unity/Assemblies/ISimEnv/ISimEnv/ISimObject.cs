using UnityEngine;
using UnityEngine.Events;

namespace ISimEnv {
    public interface ISimObject {
        GameObject GameObject { get; }
        string Name { get; }
        void Initialize();
        void Interact(params object[] args);
        void Deinitialize();
    }
}
