using ISimEnv;

namespace SimEnv {
    public class ManagersWrapper : IManagers {
        public ILoading loading => LoadingManager.instance.loadingWrapper;
    }
}