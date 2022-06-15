using UnityEngine;
using UnityEngine.Events;

namespace ISimEnv {
    /// <summary>
    /// High-level API for cameras.
    /// <para>Do not extend. Instead, to add functionality, add a custom component to the referenced <c>node.gameObject</c>.</para>
    /// </summary>
    public interface ICamera {
        /// <summary>
        /// The node this Camera is attached to.
        /// </summary>
        INode node { get; }

        /// <summary>
        /// The corresponding <c>UnityEngine.Camera</c> component.
        /// </summary>
        Camera camera { get; }

        /// <summary>
        /// Render the camera and return the resulting color buffer.
        /// </summary>
        /// <param name="callback"></param>
        void Render(UnityAction<Color32[]> callback);
    }
}