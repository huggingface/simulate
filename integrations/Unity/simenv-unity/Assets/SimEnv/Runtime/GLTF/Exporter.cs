using UnityEngine;
using System;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Linq;
using System.IO;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace SimEnv.GLTF {
    public static class Exporter {
#if UNITY_EDITOR
        [MenuItem("GameObject/SimEnv/Export GLB")]
        public static void ExportSelectedGLB() {
            string filepath = EditorUtility.SaveFilePanel("Export GLB", "", "scene", "glb");
            ExportGLB(Selection.activeGameObject, filepath);
        }

        [MenuItem("GameObject/SimEnv/Export GLTF")]
        public static void ExportSelectedGLTF() {
            string filepath = EditorUtility.SaveFilePanel("Export GLTF", "", "scene", "gltf");
            ExportGLTF(Selection.activeGameObject, filepath);
        }
#endif

        public static void ExportGLB(GameObject root, string filepath) {
            GLTFObject gltfObject = CreateGLTFObject(root.transform, filepath);
            JsonSerializerSettings settings = new JsonSerializerSettings() {
                NullValueHandling = NullValueHandling.Ignore
            };
            string content = JsonConvert.SerializeObject(gltfObject, settings);
            throw new NotImplementedException();
        }

        public static void ExportGLTF(GameObject root, string filepath) {
            GLTFObject gltfObject = CreateGLTFObject(root.transform, filepath);
            JsonSerializerSettings settings = new JsonSerializerSettings() {
                NullValueHandling = NullValueHandling.Ignore
            };
            string content = JsonConvert.SerializeObject(gltfObject, settings);
            File.WriteAllText(filepath, content);
        }

        public static GLTFObject CreateGLTFObject(Transform root, string filepath) {
            byte[] bufferData = new byte[0];
            Dictionary<string, GLTFImage.ExportResult> imageDict = new Dictionary<string, GLTFImage.ExportResult>();

            GLTFAsset asset = new GLTFAsset() { generator = "SimEnv-Unity", version = "2.0" };
            GLTFObject gltfObject = new GLTFObject() { asset = asset };
            List<GLTFNode.ExportResult> nodes = GLTFNode.Export(gltfObject, root);
            GLTFScene.Export(gltfObject, nodes);
            List<GLTFMesh.ExportResult> meshes = GLTFMesh.Export(gltfObject, nodes, ref bufferData);
            GLTFMaterial.Export(gltfObject, imageDict, meshes, filepath);
            GLTFImage.Export(gltfObject, imageDict);
            KHRLightsPunctual.Export(gltfObject, nodes);
            HFColliders.Export(gltfObject, nodes);
            HFRigidBodies.Export(gltfObject, nodes);
            GLTFBuffer.Export(gltfObject, bufferData, filepath);

            return gltfObject;
        }

        public static int WriteVec2(Vector2[] data, GLTFObject gltfObject, ref byte[] bufferData) {
            GLTFAccessor accessor = new();
            accessor.type = AccessorType.VEC2;
            accessor.componentType = GLType.FLOAT;
            accessor.count = data.Length;
            float[] floatArray = new float[data.Length * 2];
            for (int i = 0; i < data.Length; i++) {
                floatArray[i * 2] = data[i].x;
                floatArray[i * 2 + 1] = data[i].y;
            }
            float[] min = new float[2];
            float[] max = new float[2];
            min[0] = data.Min(v => v.x);
            min[1] = data.Min(v => v.y);
            max[0] = data.Max(v => v.x);
            max[1] = data.Max(v => v.y);
            accessor.min = min;
            accessor.max = max;
            byte[] bytes = new byte[floatArray.Length * sizeof(float)];
            Buffer.BlockCopy(floatArray, 0, bytes, 0, bytes.Length);
            PadBuffer(accessor.type, accessor.componentType, ref bufferData);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        public static int WriteVec3(Vector3[] data, GLTFObject gltfObject, ref byte[] bufferData) {
            GLTFAccessor accessor = new GLTFAccessor();
            accessor.type = AccessorType.VEC3;
            accessor.componentType = GLType.FLOAT;
            accessor.count = data.Length;
            float[] floatArray = new float[data.Length * 3];
            for (int i = 0; i < data.Length; i++) {
                floatArray[i * 3] = data[i].x;
                floatArray[i * 3 + 1] = data[i].y;
                floatArray[i * 3 + 2] = data[i].z;
            }
            float[] min = new float[3];
            float[] max = new float[3];
            min[0] = data.Min(v => v.x);
            min[1] = data.Min(v => v.y);
            min[2] = data.Min(v => v.z);
            max[0] = data.Max(v => v.x);
            max[1] = data.Max(v => v.y);
            max[2] = data.Max(v => v.z);
            accessor.min = min;
            accessor.max = max;
            byte[] bytes = new byte[floatArray.Length * sizeof(float)];
            Buffer.BlockCopy(floatArray, 0, bytes, 0, bytes.Length);
            PadBuffer(accessor.type, accessor.componentType, ref bufferData);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        public static int WriteVec4(Vector4[] data, GLTFObject gltfObject, ref byte[] bufferData) {
            GLTFAccessor accessor = new GLTFAccessor();
            accessor.type = AccessorType.VEC4;
            accessor.componentType = GLType.FLOAT;
            accessor.count = data.Length;
            float[] floatArray = new float[data.Length * 4];
            for (int i = 0; i < data.Length; i++) {
                floatArray[i * 4] = data[i].x;
                floatArray[i * 4 + 1] = data[i].y;
                floatArray[i * 4 + 2] = data[i].z;
                floatArray[i * 4 + 3] = data[i].w;
            }
            float[] min = new float[4];
            float[] max = new float[4];
            min[0] = data.Min(v => v.x);
            min[1] = data.Min(v => v.y);
            min[2] = data.Min(v => v.z);
            min[3] = data.Min(v => v.w);
            max[0] = data.Max(v => v.x);
            max[1] = data.Max(v => v.y);
            max[2] = data.Max(v => v.z);
            max[3] = data.Max(v => v.w);
            accessor.min = min;
            accessor.max = max;
            byte[] bytes = new byte[floatArray.Length * sizeof(float)];
            Buffer.BlockCopy(floatArray, 0, bytes, 0, bytes.Length);
            PadBuffer(accessor.type, accessor.componentType, ref bufferData);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        public static int WriteInt(int[] data, GLTFObject gltfObject, ref byte[] bufferData) {
            GLTFAccessor accessor = new GLTFAccessor();
            accessor.type = AccessorType.SCALAR;
            accessor.componentType = GLType.UNSIGNED_SHORT;
            accessor.count = data.Length;
            accessor.min = new float[] { data.Min() };
            accessor.max = new float[] { data.Max() };
            byte[] bytes = new byte[data.Length * sizeof(ushort)];
            ushort[] shortArray = Array.ConvertAll(data, x => (ushort)x);
            Buffer.BlockCopy(shortArray, 0, bytes, 0, bytes.Length);
            PadBuffer(accessor.type, accessor.componentType, ref bufferData);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        static void PadBuffer(AccessorType accessorType, GLType componentType, ref byte[] bufferData) {
            int componentSize = accessorType.ComponentCount() * componentType.ByteSize();
            int padSize = bufferData.Length % componentSize;
            Array.Resize(ref bufferData, bufferData.Length + padSize);
        }

        public static int WriteToBuffer(byte[] newData, GLTFObject gltfObject, ref byte[] bufferData) {
            int byteOffset = bufferData.Length;
            int byteLength = newData.Length;
            Array.Resize(ref bufferData, byteOffset + byteLength);
            newData.CopyTo(bufferData, byteOffset);
            GLTFBufferView bufferView = new GLTFBufferView();
            bufferView.buffer = 0; // Always exports to a single buffer
            bufferView.byteOffset = byteOffset;
            bufferView.byteLength = byteLength;
            gltfObject.bufferViews ??= new List<GLTFBufferView>();
            gltfObject.bufferViews.Add(bufferView);
            int bufferViewID = gltfObject.bufferViews.Count - 1;
            return bufferViewID;
        }
    }
}