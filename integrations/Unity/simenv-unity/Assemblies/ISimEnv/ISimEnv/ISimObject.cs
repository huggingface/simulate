using UnityEngine;
using UnityEngine.Events;

namespace ISimEnv {
    /// <summary>
    /// Interface required by every tracked SimEnv object
    /// </summary>
    public interface ISimObject {
        event UnityAction<ISimObject> OnDeinitialize;
        GameObject GameObject { get; }
        string Name { get; }
    }
}
