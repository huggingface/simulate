namespace ISimEnv {
    public interface ILoading {
        IManagers managers { get; }
        bool loadingComplete { get; }
    }
}