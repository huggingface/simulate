namespace ISimEnv {
    public interface ISimulation {
        IManagers managers { get; }
        bool TryGetNode(string name, out INode node);
    }
}