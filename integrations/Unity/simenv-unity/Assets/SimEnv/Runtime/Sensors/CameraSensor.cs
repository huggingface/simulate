using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Rendering.Universal;

namespace SimEnv {
    public class CameraSensor : ISensor {
        public static string mName = "CameraSensor";
        public static string mType = "uint8";
        public Node node => m_node;
        public Camera camera => m_camera;
        Texture2D tex;
        Camera m_camera;
        Node m_node;

        public CameraSensor(Node node, SimEnv.GLTF.HFCameraSensors.HFCameraSensor data) {
            m_node = node;

            m_camera = node.gameObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.gray;
            camera.targetTexture = new RenderTexture(data.width, data.height, 24, RenderTextureFormat.Default);
            camera.targetTexture.name = "RenderTexture";
            switch (data.type) {
                case GLTF.CameraType.orthographic:
                    camera.orthographic = true;
                    camera.nearClipPlane = data.orthographic.znear;
                    camera.farClipPlane = data.orthographic.zfar;
                    camera.orthographicSize = data.orthographic.ymag;
                    break;
                case GLTF.CameraType.perspective:
                    camera.orthographic = false;
                    camera.nearClipPlane = data.perspective.znear;
                    if (data.perspective.zfar.HasValue)
                        camera.farClipPlane = data.perspective.zfar.Value;
                    if (data.perspective.aspectRatio.HasValue)
                        camera.aspect = data.perspective.aspectRatio.Value;
                    camera.fieldOfView = Mathf.Rad2Deg * data.perspective.yfov;
                    break;
            }
            UniversalAdditionalCameraData cameraData = camera.gameObject.AddComponent<UniversalAdditionalCameraData>();
            cameraData.renderPostProcessing = true;
            camera.enabled = false;
            tex = new Texture2D(camera.targetTexture.width, camera.targetTexture.height);
            node.sensor = this;
            if (Application.isPlaying)
                Simulator.Register(this);
        }
        public string GetName() {
            return mName;
        }
        public string GetSensorType() {
            return mType;
        }
        public int GetSize() {
            return camera.targetTexture.width * camera.targetTexture.height * 3;
        }

        public int[] GetShape() {
            int[] shape = { camera.targetTexture.height, camera.targetTexture.width, 3 };
            return shape;
        }
        public string GetBufferType() {
            return "uint";
        }

        public IEnumerator GetObs(SensorBuffer buffer, int index) {
            camera.enabled = true; // Enable camera so that it renders in Unity's internal render loop
            yield return new WaitForEndOfFrame(); // Wait for Unity to render
            CopyRenderResultToColorBuffer(buffer, index);
            camera.enabled = false; // Disable camera for performance
        }

        private void CopyRenderResultToColorBuffer(SensorBuffer buffer, int index) {
            RenderTexture activeRenderTexture = RenderTexture.active;
            RenderTexture.active = camera.targetTexture;
            tex.ReadPixels(new Rect(0, 0, tex.width, tex.height), 0, 0);
            tex.Apply();
            Color32[] pixels = tex.GetPixels32();
            for (int i = 0; i < pixels.Length; i++) {
                buffer.uintBuffer[index + i * 3] = pixels[i].r;
                buffer.uintBuffer[index + i * 3 + 1] = pixels[i].g;
                buffer.uintBuffer[index + i * 3 + 2] = pixels[i].b;
            }
        }
    }
}