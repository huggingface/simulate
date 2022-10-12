using System.Collections.Generic;

namespace Simulate {
    /// <summary>
    /// Interface for custom GLTF extensions.
    /// <para>Extensions defined should be serializable, so they can be passed as json strings.</para>
    /// <example>
    /// For example, a GLTF extension that adds a RigidBody with a given mass:
    /// <code>
    /// [Serializable]
    /// public class MyCustomRigidBodyExtension : IGLTFExtension {
    ///     public float mass;
    ///     
    ///     public void Initialize(Node node, Dictionary<string, object> kwargs) {
    ///         Rigidbody rigidBody = node.gameObject.AddComponent{Rigidbody}();
    ///         rigidBody.mass = mass;
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
        void Initialize(Node node, Dictionary<string, object> kwargs);
    }
}