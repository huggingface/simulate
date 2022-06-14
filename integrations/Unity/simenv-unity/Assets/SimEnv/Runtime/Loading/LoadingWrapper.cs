using ISimEnv;

namespace SimEnv {
    public class LoadingWrapper : ILoading {
        public IManagers managers => SimulationManager.instance.managersWrapper;
        public bool loadingComplete => SimulationManager.instance.updateMode == SimulationManager.UpdateMode.Default;
    }
}