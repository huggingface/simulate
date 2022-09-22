// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFPrimitive.cs
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Simulate.GLTF {
    public class GLTFPrimitive {
        [JsonProperty(Required = Required.Always)] public GLTFAttributes attributes;
        public RenderingMode mode = RenderingMode.TRIANGLES;
        public int? indices;
        public int? material;
        public List<GLTFAttributes> targets;
        public Extensions extensions;

        public class GLTFAttributes {
            public int? POSITION;
            public int? NORMAL;
            public int? TANGENT;
            public int? COLOR_0;
            public int? TEXCOORD_0;
            public int? TEXCOORD_1;
            public int? TEXCOORD_2;
            public int? TEXCOORD_3;
            public int? TEXCOORD_4;
            public int? TEXCOORD_5;
            public int? TEXCOORD_6;
            public int? TEXCOORD_7;
            public int? JOINTS_0;
            public int? JOINTS_1;
            public int? JOINTS_2;
            public int? JOINTS_3;
            public int? WEIGHTS_0;
            public int? WEIGHTS_1;
            public int? WEIGHTS_2;
            public int? WEIGHTS_3;
        }

        public class Extensions {
            public DracoMeshCompression KHR_draco_mesh_compression;
        }

        public class DracoMeshCompression {
            public int bufferView = 0;
            public GLTFAttributes attributes;
        }
    }
}