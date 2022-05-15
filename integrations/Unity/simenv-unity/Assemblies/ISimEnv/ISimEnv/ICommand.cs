using UnityEngine.Events;

namespace ISimEnv {
    public abstract class ICommand {
        public abstract void Execute(UnityAction<string> callback);
    }
}