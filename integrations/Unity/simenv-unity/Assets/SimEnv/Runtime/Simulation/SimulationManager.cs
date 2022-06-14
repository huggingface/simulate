using UnityEngine;
using System.Collections.Generic;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Simulation Manager")]
    public class SimulationManager : Singleton<SimulationManager> {
        public static readonly int FRAME_RATE = 30;
        public static readonly int FRAME_SKIP = 4;
        public static readonly float FRAME_INTERVAL = 1f / FRAME_RATE;

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

        public void Register(ISimulationManager manager) {
            if(!managers.Contains(manager))
                managers.Add(manager);
        }

        public void Step() {
            for(int i = 0; i < FRAME_SKIP; i++)
                Physics.Simulate(FRAME_INTERVAL);
            for(int i = 0; i < managers.Count; i++)
                managers[i].Step();
        }

        public enum UpdateMode {
            Undefined,
            Default,
            Loading,
            Unloading
        }
    }
}