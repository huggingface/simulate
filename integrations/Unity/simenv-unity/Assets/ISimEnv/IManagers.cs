namespace ISimEnv {
    public interface IManagers {
        ILoading loading { get; }
        ISimulation simulation { get; }
        IAgents agents { get; }
    }
}