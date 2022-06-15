using UnityEngine;

namespace ISimEnv {
    public interface INode {
        string name { get; }
        Vector3 position { get; }
        Quaternion rotation { get; }
        void Release();
    }
}