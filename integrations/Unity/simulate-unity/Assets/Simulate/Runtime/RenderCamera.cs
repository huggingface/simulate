using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Simulate {
    public class RenderCamera {
        public Node node => m_node;
        public UnityEngine.Camera camera => m_camera;
        public bool readable { get; private set; }

        Texture2D tex;
        UnityEngine.Camera m_camera;
        Node m_node;

        public RenderCamera(Node node, GLTF.GLTFCamera data) {
            m_node = node;

            m_camera = node.gameObject.AddComponent<UnityEngine.Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.gray;
            camera.targetTexture = new RenderTexture(data.width, data.height, 24, RenderTextureFormat.ARGB32);
            camera.targetTexture.filterMode = FilterMode.Point;
            camera.targetTexture.antiAliasing = 1;
            camera.targetTexture.name = "RenderTexture";
            switch (data.type) {
                case GLTF.CameraType.orthographic:
                    camera.orthographic = true;
                    if (data.orthographic.znear.HasValue)
                        camera.nearClipPlane = data.orthographic.znear.Value;
                    if (data.orthographic.zfar.HasValue)
                        camera.farClipPlane = data.orthographic.zfar.Value;
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
            // TODO: Add post processing and antialiasing parameters
            cameraData.renderPostProcessing = false;
            cameraData.antialiasing = AntialiasingMode.None;
            camera.enabled = false;
            readable = Config.instance.returnFrames
                && (Config.instance.cameraFilter == null || Config.instance.cameraFilter.Contains(node.name));
            tex = new Texture2D(camera.targetTexture.width, camera.targetTexture.height);
        }

        public void CopyRenderResultToBuffer(out uint[,,] buffer) {
            RenderTexture activeRenderTexture = RenderTexture.active;
            RenderTexture.active = camera.targetTexture;
            tex.ReadPixels(new Rect(0, 0, tex.width, tex.height), 0, 0);
            tex.Apply();
            // Todo: More efficient method, such as pointing to the texture on the GPU
            // Currently, GetPixels32 copies the texture from GPU to CPU, which is slow
            // See https://docs.unity3d.com/ScriptReference/Texture2D.GetRawTextureData.html
            int x, y;
            Color32[] colors = tex.GetPixels32();
            RenderTexture.active = activeRenderTexture;
            // Reshape to B,C,H,W
            buffer = new uint[3, tex.height, tex.width];
            for (int i = 0; i < colors.Length; i++) {
                x = i % tex.width;
                y = tex.height - 1 - Mathf.FloorToInt(i / (float)tex.width);
                buffer[0, y, x] = colors[i].r;
                buffer[1, y, x] = colors[i].g;
                buffer[2, y, x] = colors[i].b;
            }
        }
    }
}