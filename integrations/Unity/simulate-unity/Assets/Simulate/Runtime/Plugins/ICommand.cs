using System.Collections.Generic;
using UnityEngine.Events;

namespace Simulate {
    /// <summary>
    /// Interface for defining custom API commands.
    /// <para>Serializable fields in custom commands can be passed through the python API.</para>
    /// <example>
    /// For example, on the Unity side:
    /// <code>
    /// public class MyCustomLoggingCommand : ICommand {
    ///     public string message;
    ///     
    ///     public void Execute(UnityAction{string} callback) {
    ///         Debug.Log("Received message: " + message);
    ///         callback("{}");
    ///     }
    /// }
    /// </code>
    /// Then, on the python side, given a scene using the Unity engine:
    /// <code>
    /// command = {
    ///     "type": "MyCustomLoggingCommand", 
    ///     "contents": json.dumps({
    ///         "message": "hello from python api"}
    ///     )}
    /// }
    /// scene.engine.run_command(command)
    /// </code>
    /// </example>
    /// </summary>
    public interface ICommand {
        /// <summary>
        /// Executes the custom command.
        /// <para>Don't forget to call the callback, i.e. <c>callback("{}");</c>.</para>
        /// </summary>
        /// <param name="callback">Required callback for the client to continue execution.</param>
        void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback);
    }
}