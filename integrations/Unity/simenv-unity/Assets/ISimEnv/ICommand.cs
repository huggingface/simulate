using UnityEngine.Events;

namespace ISimEnv {
    public interface ICommand {
        void Execute(UnityAction<string> callback);
    }
}