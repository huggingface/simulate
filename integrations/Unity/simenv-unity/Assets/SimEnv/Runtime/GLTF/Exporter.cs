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
            GLTFAsset asset = new GLTFAsset() {
                generator = "SimEnv-Unity",
                version = "2.0"
            };
            List<GLTFNode.ExportResult> nodes = GLTFNode.Export(root);
            List<GLTFMesh.ExportResult> meshes = GLTFMesh.Export(nodes);

            GLTFObject gltfObject = new GLTFObject() {
                scene = 0,
                asset = asset,
                nodes = nodes.Cast<GLTFNode>().ToList(),
                meshes = meshes.Cast<GLTFMesh>().ToList(),
                scenes = new List<GLTFScene>()
            };

            GLTFScene scene = new GLTFScene();
            scene.nodes = new List<int>();
            for(int i = 0; i < nodes.Count; i++)
                if(nodes[i].transform.parent == null)
                    scene.nodes.Add(i);
            gltfObject.scenes.Add(scene);

            byte[] bufferData = new byte[0];
            for(int i = 0; i < meshes.Count; i++) {
                GLTFMesh.ExportResult mesh = meshes[i];
                for(int j = 0; j < mesh.primitives.Count; j++) {
                    GLTFPrimitive primitive = mesh.primitives[j];
                    GLTFPrimitive.GLTFAttributes attributes = new GLTFPrimitive.GLTFAttributes();
                    if(mesh.mesh.vertices != null && mesh.mesh.vertices.Length > 0)
                        attributes.POSITION = WriteVec3(mesh.mesh.vertices, gltfObject, ref bufferData);
                    if(mesh.mesh.normals != null && mesh.mesh.normals.Length > 0)
                        attributes.NORMAL = WriteVec3(mesh.mesh.normals, gltfObject, ref bufferData);
                    if(mesh.mesh.triangles != null && mesh.mesh.triangles.Length > 0)
                        primitive.indices = WriteInt(mesh.mesh.triangles, gltfObject, ref bufferData);
                    primitive.attributes = attributes;
                }
            }

            nodes.ForEach(node => HF_collider.Export(node));

            List<GLTFMaterial.ExportResult> materials = GLTFMaterial.Export(meshes);
            if(materials.Count > 0) {
                gltfObject.materials = new List<GLTFMaterial>();
                for(int i = 0; i < materials.Count; i++) {
                    GLTFMaterial.ExportResult result = materials[i];
                    Material material = result.material;
                    if(material.mainTexture != null)
                        throw new NotImplementedException();
                    GLTFMaterial.PbrMetallicRoughness pbrMetallicRoughness = new GLTFMaterial.PbrMetallicRoughness();
                    pbrMetallicRoughness.baseColorFactor = material.color;
                    // TODO: material properties
                    result.pbrMetallicRoughness = pbrMetallicRoughness;
                }
            }
            gltfObject.materials = materials.Cast<GLTFMaterial>().ToList();

            GLTFBuffer buffer = new GLTFBuffer();
            buffer.byteLength = bufferData.Length;
            string bufferPath = filepath.Replace(".gltf", ".bin");
            buffer.uri = Path.GetFileName(bufferPath);
            if(gltfObject.buffers == null)
                gltfObject.buffers = new List<GLTFBuffer>();
            gltfObject.buffers.Add(buffer);
            File.WriteAllBytes(bufferPath, bufferData);

            return gltfObject;
        }

        static int WriteVec3(Vector3[] data, GLTFObject gltfObject, ref byte[] bufferData, bool normalized = false, int bufferID = 0) {
            GLTFAccessor accessor = new GLTFAccessor();
            accessor.type = AccessorType.VEC3;
            accessor.componentType = GLType.FLOAT;
            accessor.count = data.Length;
            float[] floatArray = new float[data.Length * 3];
            for(int i = 0; i < data.Length; i++) {
                floatArray[i * 3] = data[i].x;
                floatArray[i * 3 + 1] = data[i].y;
                floatArray[i * 3 + 2] = data[i].z;
            }
            float[] min = new float[3];
            float[] max = new float[3];
            min[0] = data.Min(x => x.x);
            min[1] = data.Min(x => x.y);
            min[2] = data.Min(x => x.z);
            max[0] = data.Max(x => x.x);
            max[1] = data.Max(x => x.y);
            max[2] = data.Max(x => x.z);
            accessor.min = min;
            accessor.max = max;
            byte[] bytes = new byte[floatArray.Length * sizeof(float)];
            Buffer.BlockCopy(floatArray, 0, bytes, 0, bytes.Length);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            if(gltfObject.accessors == null)
                gltfObject.accessors = new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        static int WriteInt(int[] data, GLTFObject gltfObject, ref byte[] bufferData, int bufferID = 0) {
            GLTFAccessor accessor = new GLTFAccessor();
            accessor.type = AccessorType.SCALAR;
            accessor.componentType = GLType.UNSIGNED_SHORT;
            accessor.count = data.Length;
            accessor.min = new float[] { data.Min() };
            accessor.max = new float[] { data.Max() };
            byte[] bytes = new byte[data.Length * sizeof(ushort)];
            ushort[] shortArray = Array.ConvertAll(data, x => checked((ushort)x));
            Buffer.BlockCopy(shortArray, 0, bytes, 0, bytes.Length);
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            if(gltfObject.accessors == null)
                gltfObject.accessors = new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        static int WriteToBuffer(byte[] newData, GLTFObject gltfObject, ref byte[] bufferData, int bufferID = 0) {
            int byteOffset = bufferData.Length;
            int byteLength = newData.Length;
            Array.Resize(ref bufferData, byteOffset + byteLength);
            newData.CopyTo(bufferData, byteOffset);
            GLTFBufferView bufferView = new GLTFBufferView();
            bufferView.buffer = bufferID;
            bufferView.byteOffset = byteOffset;
            bufferView.byteLength = byteLength;
            if(gltfObject.bufferViews == null)
                gltfObject.bufferViews = new List<GLTFBufferView>();
            gltfObject.bufferViews.Add(bufferView);
            int bufferViewID = gltfObject.bufferViews.Count - 1;
            return bufferViewID;
        }
    }
}