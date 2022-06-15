using UnityEngine;
using System.Collections.Generic;
using ISimEnv;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Simulation Manager")]
    public class SimulationManager : ManagerBase<SimulationManager, SimulationProperties> {
        ManagersWrapper _managersWrapper;
        public ManagersWrapper managersWrapper {
            get {
                _managersWrapper ??= new ManagersWrapper();
                return _managersWrapper;
            }
        }

        SimulationWrapper _simulationWrapper;
        public SimulationWrapper simulationWrapper {
            get {
                _simulationWrapper ??= new SimulationWrapper();
                return _simulationWrapper;
            }
        }

        Dictionary<string, INode> _nodes;
        public Dictionary<string, INode> nodes {
            get {
                _nodes ??= new Dictionary<string, INode>();
                return _nodes;
            }
        }

        List<ISimulationManager> _managers;
        public List<ISimulationManager> managers {
            get {
                _managers ??= new List<ISimulationManager>();
                return _managers;
            }
        }

        public UpdateMode updateMode;
        public float frameSkip;
        public float frameInterval;

        public override void InitializeProperties(SimulationProperties properties = null) {
            properties ??= Resources.LoadAll<SimulationProperties>("Properties")[0];
            frameSkip = properties.frameSkip;
            frameInterval = properties.frameInterval;
            nodes.Clear();
        }

        public void Register(ISimulationManager manager) {
            if(!managers.Contains(manager))
                managers.Add(manager);
        }

        public void Register(INode node) {
            if(nodes.TryGetValue(node.name, out INode existing)) {
                Debug.LogWarning($"Node with name {node.name} already existings. Replacing.");
                node.Release();
            }
            nodes[node.name] = node;
        }

        public void Step() {
            for(int i = 0; i < frameSkip; i++) {
                Physics.Simulate(frameInterval);
                for(int j = 0; j < managers.Count; j++)
                    managers[j].Step();
            }
        }

        public enum UpdateMode {
            Undefined,
            Default,
            Loading,
            Unloading
        }
    }
}