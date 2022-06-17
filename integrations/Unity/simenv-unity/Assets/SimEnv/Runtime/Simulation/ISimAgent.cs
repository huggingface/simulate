using UnityEngine;

namespace ISimEnv {
    public interface ISimAgent {
        GameObject GameObject { get; }
        string Name { get; }
    }
}
