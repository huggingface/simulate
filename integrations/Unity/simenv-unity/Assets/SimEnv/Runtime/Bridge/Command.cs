using System;
using System.Linq;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public abstract class Command : PolymorphicObject {
        public static Command Parse(string commandWrapperJson) {
            CommandWrapper wrapper = JsonUtility.FromJson<CommandWrapper>(commandWrapperJson);
            Type commandType = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => x.IsSubclassOf(typeof(Command)))
                .FirstOrDefault(x => x.ToString() == "SimEnv." + wrapper.type);
            if(commandType == null)
                throw new NotImplementedException("Uknown command: " + wrapper.type);
            Command command = JsonUtility.FromJson(wrapper.contents, commandType) as Command;
            return command;
        }

        public abstract void Execute(UnityAction<string> callback);
    }

    [Serializable]
    public class CommandWrapper {
        public string type;
        public string contents;
    }
}