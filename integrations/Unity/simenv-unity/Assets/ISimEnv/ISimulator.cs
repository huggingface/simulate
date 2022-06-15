using System.Collections.Generic;

namespace ISimEnv {
    /// <summary>
    /// High-level API for the simulator.
    /// </summary>
    public interface ISimulator {
        /// <summary>
        /// Returns a collection of all tracked cameras.
        /// </summary>
        /// <returns></returns>
        IEnumerable<ICamera> GetCameras();

        /// <summary>
        /// Returns a collection of all tracked nodes.
        /// </summary>
        /// <returns></returns>
        IEnumerable<INode> GetNodes();

        /// <summary>
        /// Find a tracked node by name.
        /// </summary>
        /// <param name="name">The unique name of the node.</param>
        /// <param name="node">If true, stores reference to the located node.</param>
        /// <returns>Returns true if the node was found, otherwise false.</returns>
        bool TryGetNode(string name, out INode node);
    }
}