using System.Collections.Generic;
using ISimEnv;

namespace SimEnv {
    public class SimulatorWrapper : ISimulator {
        public IEnumerable<ICamera> GetCameras() {
            return RenderManager.instance.cameras;
        }

        public IEnumerable<INode> GetNodes() {
            return SimulationManager.instance.nodes.Values;
        }

        public bool TryGetNode(string name, out INode node) {
            return SimulationManager.instance.nodes.TryGetValue(name, out node);
        }
    }
}