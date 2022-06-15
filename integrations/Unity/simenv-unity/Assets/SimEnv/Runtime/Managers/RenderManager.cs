using System.Collections;
using System.Collections.Generic;
using ISimEnv;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Render Manager")]
    public class RenderManager : Singleton<RenderManager> {
        List<ICamera> _cameras;
        /// <summary>
        /// Stores reference to all tracked cameras in the current environment.
        /// </summary>
        public List<ICamera> cameras {
            get {
                _cameras ??= new List<ICamera>();
                return _cameras;
            }
        }

        /// <summary>
        /// Register a camera to be called by <c>Render</c>.
        /// </summary>
        /// <param name="camera"></param>
        public void Register(ICamera camera) {
            if(!cameras.Contains(camera))
                cameras.Add(camera);
        }

        /// <summary>
        /// Render all cameras and returns their color buffers.
        /// </summary>
        /// <param name="callback">List of camera color buffers.</param>
        public void Render(UnityAction<List<Color32[]>> callback) {
            RenderCoroutine(callback).RunCoroutine();
        }

        private IEnumerator RenderCoroutine(UnityAction<List<Color32[]>> callback) {
            List<Color32[]> buffers = new List<Color32[]>();
            for(int i = 0; i < cameras.Count; i++)
                cameras[i].Render(buffer => buffers.Add(buffer));
            yield return new WaitUntil(() => buffers.Count == cameras.Count);
            callback(buffers);
        }
    }
}