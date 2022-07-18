using SimEnv;

namespace Cartpole {
    public class CartpolePlugin : IPlugin {
        public void OnCreated() {
            CartpoleManager.instance = new CartpoleManager();
        }

        public void OnReleased() {
            
        }

        public void OnEnvironmentLoaded(Environment environment) {
            
        }

        public void OnBeforeEnvironmentUnloaded(Environment environment) {
            
        }
    }
}