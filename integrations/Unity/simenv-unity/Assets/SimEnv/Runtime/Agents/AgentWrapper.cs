using System.Collections.Generic;
using System.Linq;
using ISimEnv;

namespace SimEnv {
    public class AgentWrapper : IAgents {
        public IManagers managers => SimulationManager.instance.managersWrapper;

        public IEnumerable<IAgent> GetAgents() {
            return AgentManager.instance.agents.Cast<IAgent>();
        }
    }
}