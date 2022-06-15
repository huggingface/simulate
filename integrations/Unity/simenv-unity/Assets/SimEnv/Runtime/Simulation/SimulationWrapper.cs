using ISimEnv;

namespace SimEnv {
    public class SimulationWrapper : ISimulation {
        public IManagers managers => SimulationManager.instance.managersWrapper;

        public bool TryGetNode(string name, out INode node) {
            return SimulationManager.instance.nodes.TryGetValue(name, out node);
        }
    }
}