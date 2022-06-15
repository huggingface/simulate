using UnityEngine;
using System.Collections.Generic;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Simulation Manager")]
    public class SimulationManager : ManagerBase<SimulationManager, SimulationProperties> {
        ManagersWrapper _managersWrapper;
        public ManagersWrapper managersWrapper {
            get {
                _managersWrapper ??= new ManagersWrapper();
                return _managersWrapper;
            }
        }

        List<ISimulationManager> _managers;
        List<ISimulationManager> managers {
            get {
                _managers ??= new List<ISimulationManager>();
                return _managers;
            }
        }

        public UpdateMode updateMode;
        public float frameSkip;
        public float frameInterval;

        public override void InitializeProperties(SimulationProperties properties = null) {
            properties ??= Resources.LoadAll<SimulationProperties>("Properties")[0];
            frameSkip = properties.frameSkip;
            frameInterval = properties.frameInterval;
        }

        public void Register(ISimulationManager manager) {
            if(!managers.Contains(manager))
                managers.Add(manager);
        }

        public void Step() {
            for(int i = 0; i < frameSkip; i++) {
                Physics.Simulate(frameInterval);
                for(int j = 0; j < managers.Count; j++)
                    managers[j].Step();
            }
        }

        public enum UpdateMode {
            Undefined,
            Default,
            Loading,
            Unloading
        }
    }
}