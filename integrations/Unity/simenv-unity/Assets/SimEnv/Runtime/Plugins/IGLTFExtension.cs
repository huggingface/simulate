namespace Simulate {
    /// <summary>
    /// Interface for custom GLTF Node extensions.
    /// <para>Extensions defined should be serializable, so they can be passed as json strings.</para>
    /// <example>
    /// For example, a GLTF extension that adds a RigidBody with a given mass:
    /// <code>
    /// [Serializable]
    /// public class MyCustomRigidBodyExtension : IGLTFNodeExtension {
    ///     public float mass;
    ///     
    ///     public void Initialize(Node node) {
    ///         Rigidbody rigidBody = node.gameObject.AddComponent{Rigidbody}();
    ///         rigidBody.mass = mass;
    ///     }
    /// }
    /// </code>
    /// Then, on the Python side, this GLTF json may be passed:
    /// <code>
    /// {
    ///     "extensions": {
    ///         "custom": [
    ///             {
    ///                 "type": "MyCustomRigidBodyExtension",
    ///                 "contents": json.dumps({
    ///                     "mass": 5.0
    ///                 })
    ///             }
    ///         ]
    ///     }
    /// }
    /// </code>
    /// </example>
    /// </summary>
    public interface IGLTFExtension {
        /// <summary>
        /// Initialize extension on the given node.
        /// </summary>
        /// <param name="node"></param>
        void Initialize(Node node);
    }
}