using System.Collections;
using SimEnv.GLTF;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class SimCameraBase : MonoBehaviour {
        public GLTFCamera data;
        public Camera cam;

        private uint[] pixel_values;

        public void Initialize(GLTFCamera data) {
            this.data = data;

            pixel_values = new uint[data.width * data.height * 3];

            cam = gameObject.AddComponent<Camera>();
            cam.targetTexture = new RenderTexture(data.width, data.height, 24, RenderTextureFormat.Default);
            cam.targetTexture.name = "RenderTexture";
            transform.localRotation *= Quaternion.Euler(0, 180, 0);
            switch (data.type) {
                case GLTF.CameraType.orthographic:
                    cam.orthographic = true;
                    cam.nearClipPlane = data.orthographic.znear;
                    cam.farClipPlane = data.orthographic.zfar;
                    cam.orthographicSize = data.orthographic.ymag;
                    break;
                case GLTF.CameraType.perspective:
                    cam.orthographic = false;
                    cam.nearClipPlane = data.perspective.znear;
                    if (data.perspective.zfar.HasValue)
                        cam.farClipPlane = data.perspective.zfar.Value;
                    if (data.perspective.aspectRatio.HasValue)
                        cam.aspect = data.perspective.aspectRatio.Value;
                    cam.fieldOfView = Mathf.Rad2Deg * data.perspective.yfov;
                    break;
            }
            cam.enabled = false;
        }

        void Update() {
            //Debug.Log("on");
            if (cam.enabled)
                Debug.Log(Time.frameCount);
        }

        // public void Render(UnityAction<string> callback, uint[] pixel_values, int startingIndex) {
        //     StartCoroutine(RenderCoroutine(callback, pixel_values, startingIndex));
        // }

        public IEnumerator RenderCoroutine(uint[] pixel_values, int startingIndex) {
            cam.enabled = true; // Enable camera so that it renders in Unity's internal render loop
            yield return new WaitForEndOfFrame(); // Wait for Unity to render
            CopyRenderResultToStringBuffer(pixel_values, startingIndex);
            cam.enabled = false; // Disable camera for performance
        }

        void CopyRenderResultToStringBuffer(uint[] pixel_values, int startingIndex) {
            RenderTexture activeRenderTexture = RenderTexture.active;
            RenderTexture.active = cam.targetTexture;
            Texture2D image = new Texture2D(cam.targetTexture.width, cam.targetTexture.height);
            image.ReadPixels(new Rect(0, 0, image.width, image.height), 0, 0);
            image.Apply();
            Color32[] pixels = image.GetPixels32();
            RenderTexture.active = activeRenderTexture;

            for (int i = 0; i < pixels.Length; i++) {
                pixel_values[startingIndex + i * 3] = pixels[i].r;
                pixel_values[startingIndex + i * 3 + 1] = pixels[i].g;
                pixel_values[startingIndex + i * 3 + 2] = pixels[i].b;
                // we do not include alpha, TODO: Add option to include Depth Buffer
            }

            // //string string_array = JsonHelper.ToJson(pixel_values);
            // if (callback != null)
            //     callback("render");
        }


    }
}