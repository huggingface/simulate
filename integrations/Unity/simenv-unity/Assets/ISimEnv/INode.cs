using UnityEngine;

namespace ISimEnv {
    /// <summary>
    /// High-level API for all objects tracked by the simulator.
    /// <para>Do not extend. Instead, to add functionality, add a custom component to the referenced <c>gameObject</c>.</para>
    /// </summary>
    public interface INode {
        /// <summary>
        /// The unique name of the node.
        /// </summary>
        string name { get; }

        /// <summary>
        /// The Unity <c>GameObject</c> this node is attached to.
        /// </summary>
        GameObject gameObject { get; }

        /// <summary>
        /// Safely destroys the node.
        /// </summary>
        void Release();
    }
}