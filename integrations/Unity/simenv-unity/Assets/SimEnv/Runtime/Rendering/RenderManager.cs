using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Render Manager")]
    public class RenderManager : Singleton<RenderManager> {
        List<RenderCamera> _cameras;
        public List<RenderCamera> cameras {
            get {
                _cameras ??= new List<RenderCamera>();
                return _cameras;
            }
        }

        Dictionary<Camera, RenderCamera> _lookup;
        public Dictionary<Camera, RenderCamera> lookup {
            get {
                _lookup ??= new Dictionary<Camera, RenderCamera>();
                return _lookup;
            }
        }

        public void Register(RenderCamera camera) {
            if(!cameras.Contains(camera))
                cameras.Add(camera);
            lookup[camera.camera] = camera;
        }

        public void Render(UnityAction<List<Color32[]>> callback) {
            Simulator.instance.StartCoroutine(RenderCoroutine(callback));
        }

        public IEnumerator RenderCoroutine(UnityAction<List<Color32[]>> callback) {
            List<Color32[]> buffers = new List<Color32[]>();
            for(int i = 0; i < cameras.Count; i++)
                cameras[i].Render(buffer => buffers.Add(buffer));
            yield return new WaitUntil(() => buffers.Count == cameras.Count);
            callback(buffers);
        }
    }
}