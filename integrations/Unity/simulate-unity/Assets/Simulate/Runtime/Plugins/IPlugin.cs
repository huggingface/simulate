using System.Collections.Generic;
using System.Collections;

namespace Simulate {
    /// <summary>
    /// Used to add custom functionality to the Simulate backend.
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
    ///     public void OnStep(EventData eventData) { }
    ///     
    ///     public void OnAfterStep(EventData eventData) { }
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
        /// Called after the Simulator steps forward, before rendering.
        /// Use this for any changes that need to be applied between Simulator step and internal Unity rendering.
        /// </summary>
        /// <param name="eventData"></param>
        void OnStep(EventData eventData);

        /// <summary>
        /// Called after the Simulator steps forward.
        /// Use this to append additional event data.
        /// </summary>
        void OnAfterStep(EventData eventData);

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