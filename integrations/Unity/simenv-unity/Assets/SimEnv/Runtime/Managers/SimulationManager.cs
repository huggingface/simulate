using UnityEngine;
using System.Collections.Generic;
using ISimEnv;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Simulation Manager")]
    public class SimulationManager : Singleton<SimulationManager> {
        Dictionary<string, INode> _nodes;
        /// <summary>
        /// Stores a reference to all tracked nodes in the current environment.
        /// </summary>
        public Dictionary<string, INode> nodes {
            get {
                _nodes ??= new Dictionary<string, INode>();
                return _nodes;
            }
        }

        /// <summary>
        /// Whether the current environment is undefined, active, loading, or unloading.
        /// </summary>
        public UpdateMode updateMode;

        /// <summary>
        /// How many simulation steps to make per Step call.
        /// </summary>
        public float frameSkip = 4;

        /// <summary>
        /// Time between frames (inverse framerate).
        /// </summary>
        public float frameInterval = 30;

        public void Register(INode node) {
            if(nodes.TryGetValue(node.name, out INode existing)) {
                Debug.LogWarning($"Node with name {node.name} already existings. Replacing.");
                node.Release();
            }
            nodes[node.name] = node;
        }

        public void Step() {
            for(int i = 0; i < frameSkip; i++)
                Physics.Simulate(frameInterval);
        }

        public enum UpdateMode {
            Undefined,
            Default,
            Loading,
            Unloading
        }
    }
}