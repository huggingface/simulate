namespace SimEnv {
    /// <summary>
    /// Used to extend SimEnv with custom functionality.
    /// <para>Any classes that extend <c>ISimulatorExtension</c> will 
    /// be loaded automatically.</para>
    /// <example>
    /// Example of an extension that moves the node named "MyNode" upward:
    /// <code>
    /// public class MyCustomExtension : ISimulatorExtension {
    ///     ISimulator simulator;
    /// 
    ///     void OnCreated(ISimulator simulator) {
    ///         this.simulator = simulator;
    ///     }
    ///     
    ///     void OnReleased() { }
    ///     
    ///     void OnEnvironmentLoaded() {
    ///         simulator.TryGetNode("MyNode", out INode myNode);
    ///         myNode.gameObject.transform.position += Vector3.up;
    ///     }
    ///     
    ///     void OnEnvironmentUnloaded() { }
    /// }
    /// </code>
    /// </example>
    /// </summary>
    public interface ISimulatorExtension {
        /// <summary>
        /// Called when this extension is loaded.
        /// </summary>
        void OnCreated();

        /// <summary>
        /// Called when this extension is unloaded.
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