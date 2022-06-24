namespace SimEnv {
    /// <summary>
    /// Used to add custom functionality to the SimEnv backend.
    /// <para>Any classes that extend <c>IPlugin</c> will 
    /// be loaded automatically.</para>
    /// <example>
    /// Example of a plugin that moves the node named "MyNode" upward:
    /// <code>
    /// public class MyCustomPlugin : IPlugin {
    ///     void OnCreated() { }
    ///     
    ///     void OnReleased() { }
    ///     
    ///     void OnEnvironmentLoaded() {
    ///         Node node = Simulator.Nodes["MyNode"];
    ///         node.gameObject.transform.position += Vector3.up;
    ///     }
    ///     
    ///     void OnEnvironmentUnloaded() { }
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
        /// Called when an environment is finished loading.
        /// <para>Use this to initialize custom behaviour.</para>
        /// </summary>
        void OnEnvironmentLoaded();

        /// <summary>
        /// Called before an environment begins unloading.
        /// <para>Use this to clean up custom behaviour.</para>
        /// </summary>
        void OnBeforeEnvironmentUnloaded();
    }
}