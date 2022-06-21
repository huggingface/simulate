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
            for (int i = 0; i < nodes.Count; i++)
                if (nodes[i].transform.parent == null)
                    scene.nodes.Add(i);
            gltfObject.scenes.Add(scene);

            byte[] bufferData = new byte[0];
            for (int i = 0; i < meshes.Count; i++) {
                GLTFMesh.ExportResult mesh = meshes[i];
                for (int j = 0; j < mesh.primitives.Count; j++) {
                    GLTFPrimitive primitive = mesh.primitives[j];
                    GLTFPrimitive.GLTFAttributes attributes = new GLTFPrimitive.GLTFAttributes();
                    Vector3[] vertices = new Vector3[0];
                    if (mesh.mesh.vertices != null && mesh.mesh.vertices.Length > 0) {
                        vertices = mesh.mesh.vertices.Select(v => { v.x = -v.x; return v; }).ToArray();
                        attributes.POSITION = WriteVec3(vertices, gltfObject, ref bufferData);
                    }
                    if (mesh.mesh.normals != null && mesh.mesh.normals.Length > 0) {
                        Vector3[] normals = mesh.mesh.normals.Select(v => { v.x = -v.x; return v; }).ToArray();
                        attributes.NORMAL = WriteVec3(normals, gltfObject, ref bufferData);
                    }
                    if (mesh.mesh.tangents != null && mesh.mesh.tangents.Length > 0) {
                        Vector4[] tangents = mesh.mesh.tangents.Select(v => { v.y = -v.y; v.z = -v.z; return v; }).ToArray();
                        attributes.TANGENT = WriteVec4(tangents, gltfObject, ref bufferData);
                    }
                    // TODO: Support for multiple submeshes, alternate rendering modes
                    if (mesh.mesh.triangles != null && mesh.mesh.triangles.Length > 0) {
                        int[] triangles = mesh.mesh.triangles.Reverse().ToArray();
                        primitive.indices = WriteInt(triangles, gltfObject, ref bufferData);
                    }
                    primitive.attributes = attributes;
                }
            }

            // TODO(dylan/thom) fix collider export
            // nodes.ForEach(node => HFColliders.Export(node));

            List<GLTFMaterial.ExportResult> materials = GLTFMaterial.Export(meshes);
            Dictionary<string, GLTFImage.ExportResult> images = new Dictionary<string, GLTFImage.ExportResult>();
            if (materials.Count > 0) {
                gltfObject.materials = new List<GLTFMaterial>();
                for (int i = 0; i < materials.Count; i++) {
                    GLTFMaterial.ExportResult result = materials[i];
                    Material material = result.material;
                    GLTFMaterial.PbrMetallicRoughness pbrMetallicRoughness = new GLTFMaterial.PbrMetallicRoughness();
                    if (material.HasProperty("_Color"))
                        pbrMetallicRoughness.baseColorFactor = material.color;
                    // TODO: more material properties
                    if (material.HasProperty("_MainTex") && material.mainTexture != null) {
                        Texture2D tex = material.mainTexture as Texture2D;
                        string uri = tex.name + ".png";
                        if (!images.TryGetValue(uri, out GLTFImage.ExportResult image)) {
                            image = new GLTFImage.ExportResult();
                            image.name = tex.name;
                            image.uri = uri;
                            image.path = string.Format("{0}/{1}", Path.GetDirectoryName(filepath), uri);
                            image.bytes = tex.Decompress().EncodeToPNG();
                            image.index = images.Count;
                            images.Add(uri, image);
                        }
                        pbrMetallicRoughness.baseColorTexture = new GLTFMaterial.TextureInfo() { index = image.index };
                    }
                    result.pbrMetallicRoughness = pbrMetallicRoughness;
                }
            }
            gltfObject.materials = materials.Cast<GLTFMaterial>().ToList();

            foreach (string uri in images.Keys) {
                GLTFImage.ExportResult image = images[uri];
                File.WriteAllBytes(image.path, image.bytes);
                gltfObject.textures ??= new List<GLTFTexture>();
                gltfObject.images ??= new List<GLTFImage>();
                GLTFTexture texture = new GLTFTexture();
                texture.source = image.index;
                texture.name = image.name;
                gltfObject.textures.Add(texture);
                gltfObject.images.Add((GLTFImage)image);
            }

            GLTFBuffer buffer = new GLTFBuffer();
            buffer.byteLength = bufferData.Length;
            string bufferPath = filepath.Replace(".gltf", ".bin");
            buffer.uri = Path.GetFileName(bufferPath);
            gltfObject.buffers ??= new List<GLTFBuffer>();
            gltfObject.buffers.Add(buffer);
            File.WriteAllBytes(bufferPath, bufferData);

            return gltfObject;
        }

        static Texture2D Decompress(this Texture2D source) {
            RenderTexture renderTexture = RenderTexture.GetTemporary(
                source.width,
                source.height,
                0,
                RenderTextureFormat.Default,
                RenderTextureReadWrite.Linear
            );
            Graphics.Blit(source, renderTexture);
            RenderTexture active = RenderTexture.active;
            RenderTexture.active = renderTexture;
            Texture2D tex = new Texture2D(source.width, source.height);
            tex.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
            tex.Apply();
            RenderTexture.active = active;
            RenderTexture.ReleaseTemporary(renderTexture);
            return tex;
        }

        static int WriteVec3(Vector3[] data, GLTFObject gltfObject, ref byte[] bufferData, bool normalized = false, int bufferID = 0) {
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
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
            gltfObject.accessors.Add(accessor);
            int accessorID = gltfObject.accessors.Count - 1;
            return accessorID;
        }

        static int WriteVec4(Vector4[] data, GLTFObject gltfObject, ref byte[] bufferData, bool normalized = false, int bufferID = 0) {
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
            accessor.bufferView = WriteToBuffer(bytes, gltfObject, ref bufferData);
            gltfObject.accessors ??= new List<GLTFAccessor>();
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
            gltfObject.accessors ??= new List<GLTFAccessor>();
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
            gltfObject.bufferViews ??= new List<GLTFBufferView>();
            gltfObject.bufferViews.Add(bufferView);
            int bufferViewID = gltfObject.bufferViews.Count - 1;
            return bufferViewID;
        }
    }
}