using System.Collections.Generic;

namespace SimEnv {
    /// <summary>
    /// Used to add custom functionality to the SimEnv backend.
    /// <para>Any classes that extends <c>IPlugin</c> will 
    /// be loaded automatically.</para>
    /// <example>
    /// Example of a plugin that moves the node named "MyNode" upward:
    /// <code>
    /// public class MyCustomPlugin : IPlugin {
    ///     public void OnCreated() { }
    ///     
    ///     public void OnReleased() { }
    ///     
    ///     public void OnSceneInitialized(Dictionary<string, object> kwargs) {
    ///         Node node = Simulator.nodes["MyNode"];
    ///         node.gameObject.transform.position += Vector3.up;
    ///     }
    ///     
    ///     public void OnBeforeStep(EventData eventData) { }
    ///     
    ///     public void OnStep(EventData eventData) { }
    ///     
    ///     public void OnReset() { }
    ///     
    ///     public void OnBeforeSceneUnloaded() { }
    /// }
    /// </code>
    /// </example>
    /// </summary>
    public interface IPlugin {
        /// <summary>
        /// Called when this plugin is loaded.
        /// </summary>
        void OnCreated();

        /// <summary>
        /// Called when this plugin is unloaded.
        /// </summary>
        void OnReleased();

        /// <summary>
        /// Called when the scene is initialized.
        /// </summary>
        /// <param name="kwargs">Used to pass arbitrary keyword arguments.</param>
        void OnSceneInitialized(Dictionary<string, object> kwargs);

        /// <summary>
        /// Called before the Simulator steps forward.
        /// </summary>
        void OnBeforeStep(EventData eventData);

        /// <summary>
        /// Called after the Simulator steps forward.
        /// </summary>
        void OnStep(EventData eventData);

        /// <summary>
        /// Called when the scene is reset.
        /// </summary>
        void OnReset();

        /// <summary>
        /// Called before the scene is unloaded.
        /// </summary>
        void OnBeforeSceneUnloaded();
    }
}