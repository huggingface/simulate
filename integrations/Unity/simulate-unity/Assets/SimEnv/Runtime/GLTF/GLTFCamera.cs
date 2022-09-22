#nullable enable
// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFCamera.cs
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using UnityEngine;

namespace Simulate.GLTF {
    public class GLTFCamera {
        public Orthographic? orthographic;
        public Perspective? perspective;
        [JsonProperty(Required = Required.Always), JsonConverter(typeof(EnumConverter))] public CameraType type;
        public string? name;
        public int width = 512;
        public int height = 512;
        public Extras? extras;

        public class Orthographic {
            public float xmag = 1f;
            public float ymag = 5f;
            public float? zfar;
            public float? znear;
        }

        public class Perspective {
            public float? aspectRatio;
            [JsonProperty(Required = Required.Always)] public float yfov = 60;
            public float? zfar;
            [JsonProperty(Required = Required.Always)] public float znear = .3f;
        }

        public class Extras {
            public string? sensor_tag;
            public bool? is_actor;
        }

        public static void Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            List<GLTFCamera> components = new List<GLTFCamera>();
            foreach (GLTFNode.ExportResult node in nodes) {
                GLTFCamera? camera = StaticExport(node);
                if (camera == null) continue;
                if (!components.Contains(camera))
                    components.Add(camera);
                node.camera = components.IndexOf(camera);
            }
            if (components.Count == 0) return;
            gltfObject.cameras = components.Cast<GLTFCamera>().ToList();
            gltfObject.nodes = nodes.Cast<GLTFNode>().ToList();
        }

        static GLTFCamera? StaticExport(GLTFNode.ExportResult node) {
            Camera cam = node.transform.GetComponent<Camera>();
            if (cam == null) return null;
            GLTFCamera camera = new GLTFCamera();
            if (cam.orthographic) {
                camera.type = CameraType.orthographic;
                camera.orthographic = new Orthographic() {
                    xmag = 1f,
                    ymag = cam.orthographicSize,
                    zfar = cam.farClipPlane,
                    znear = cam.nearClipPlane,
                };
            } else {
                camera.type = CameraType.perspective;
                camera.perspective = new Perspective() {
                    aspectRatio = cam.aspect,
                    yfov = cam.fieldOfView,
                    zfar = cam.farClipPlane,
                    znear = cam.nearClipPlane,
                };
            }
            camera.name = cam.name;
            camera.width = cam.pixelWidth;
            camera.height = cam.pixelHeight;
            return camera;
        }
    }
}