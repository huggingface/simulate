namespace ISimEnv {
    public interface IManagers {
        ILoading loading { get; }
        IAgents agents { get; }
    }
}