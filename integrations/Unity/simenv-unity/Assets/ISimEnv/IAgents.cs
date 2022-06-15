using System.Collections.Generic;

namespace ISimEnv {
    public interface IAgents {
        IManagers managers { get; }
        IEnumerable<IAgent> GetAgents();
    }
}