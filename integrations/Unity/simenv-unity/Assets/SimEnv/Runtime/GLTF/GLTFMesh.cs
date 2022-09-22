// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFMesh.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Newtonsoft.Json;
using System.Threading.Tasks;
using UnityEngine.Rendering;

namespace Simulate.GLTF {
    public class GLTFMesh {
        [JsonProperty(Required = Required.Always)] public List<GLTFPrimitive> primitives;
        public List<float> weights;
        public string name;
        public Extras extras;

        public class Extras {
            public string[] targetNames;
        }

        public class ImportResult {
            public Material[] materials;
            public Mesh mesh;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            class MeshData {
                string name;
                List<Vector3> normals = new List<Vector3>();
                List<List<int>> submeshTris = new List<List<int>>();
                List<RenderingMode> submeshTrisMode = new List<RenderingMode>();
                List<Vector3> verts = new List<Vector3>();
                List<Vector4> tangents = new List<Vector4>();
                List<Color> colors = new List<Color>();
                List<BoneWeight> weights = null;
                List<Vector2> uv1 = null;
                List<Vector2> uv2 = null;
                List<Vector2> uv3 = null;
                List<Vector2> uv4 = null;
                List<Vector2> uv5 = null;
                List<Vector2> uv6 = null;
                List<Vector2> uv7 = null;
                List<Vector2> uv8 = null;
                List<BlendShape> blendShapes = new List<BlendShape>();
                List<int> submeshVertexStart = new List<int>();

                class BlendShape {
                    public string name;
                    public Vector3[] pos, norm, tan;
                }

                public MeshData(GLTFMesh gltfMesh, GLTFAccessor.ImportResult[] accessors, GLTFBufferView.ImportResult[] bufferViews) {
                    name = gltfMesh.name;
                    if (gltfMesh.primitives.Count == 0) {
                        Debug.LogWarning("0 primitives in mesh");
                    } else {
                        for (int i = 0; i < gltfMesh.primitives.Count; i++) {
                            GLTFPrimitive primitive = gltfMesh.primitives[i];
                            if (primitive.extensions != null && primitive.extensions.KHR_draco_mesh_compression != null) {
                                throw new NotImplementedException("Draco not yet supported");
                            } else {
                                int vertStartIndex = verts.Count;
                                submeshVertexStart.Add(vertStartIndex);

                                if (primitive.attributes.POSITION.HasValue) {
                                    IEnumerable<Vector3> newVerts = accessors[primitive.attributes.POSITION.Value].ReadVec3(true)
                                        .Select(v => { v.x = -v.x; return v; });
                                    verts.AddRange(newVerts);
                                }

                                int vertCount = verts.Count;

                                if (primitive.indices.HasValue) {
                                    submeshTris.Add(new List<int>(accessors[primitive.indices.Value].ReadInt().Reverse()
                                        .Select(x => x + vertStartIndex)));
                                    submeshTrisMode.Add(primitive.mode);
                                }

                                if (primitive.attributes.NORMAL.HasValue) {
                                    IEnumerable<Vector3> newNorms = accessors[primitive.attributes.NORMAL.Value].ReadVec3(true)
                                        .Select(v => { v.x = -v.x; return v; });
                                    normals.AddRange(newNorms);
                                }

                                if (primitive.attributes.TANGENT.HasValue) {
                                    IEnumerable<Vector4> newTangents = accessors[primitive.attributes.TANGENT.Value].ReadVec4(true)
                                        .Select(v => { v.y = -v.y; v.z = -v.z; return v; });
                                    tangents.AddRange(newTangents);
                                }

                                if (primitive.attributes.COLOR_0.HasValue) {
                                    colors.AddRange(accessors[primitive.attributes.COLOR_0.Value].ReadColor());
                                }

                                if (primitive.attributes.WEIGHTS_0.HasValue && primitive.attributes.JOINTS_0.HasValue) {
                                    Vector4[] weights0 = accessors[primitive.attributes.WEIGHTS_0.Value].ReadVec4(true);
                                    Vector4[] joints0 = accessors[primitive.attributes.JOINTS_0.Value].ReadVec4();
                                    if (joints0.Length == weights0.Length) {
                                        BoneWeight[] boneWeights = new BoneWeight[weights0.Length];
                                        for (int k = 0; k < boneWeights.Length; k++) {
                                            NormalizeWeights(ref weights0[k]);
                                            boneWeights[k].weight0 = weights0[k].x;
                                            boneWeights[k].weight1 = weights0[k].y;
                                            boneWeights[k].weight2 = weights0[k].z;
                                            boneWeights[k].weight3 = weights0[k].w;
                                            boneWeights[k].boneIndex0 = Mathf.RoundToInt(joints0[k].x);
                                            boneWeights[k].boneIndex1 = Mathf.RoundToInt(joints0[k].y);
                                            boneWeights[k].boneIndex2 = Mathf.RoundToInt(joints0[k].z);
                                            boneWeights[k].boneIndex3 = Mathf.RoundToInt(joints0[k].w);
                                        }
                                        if (weights == null)
                                            weights = new List<BoneWeight>(new BoneWeight[vertCount - boneWeights.Length]);
                                        weights.AddRange(boneWeights);
                                    } else {
                                        Debug.LogWarning("WEIGHTS_0 and JOINTS_0 aren't the same length. Skipped");
                                    }
                                } else {
                                    if (weights != null)
                                        weights.AddRange(new BoneWeight[vertCount - weights.Count]);
                                }

                                ReadUVs(ref uv1, accessors, primitive.attributes.TEXCOORD_0, vertCount);
                                ReadUVs(ref uv2, accessors, primitive.attributes.TEXCOORD_1, vertCount);
                                ReadUVs(ref uv3, accessors, primitive.attributes.TEXCOORD_2, vertCount);
                                ReadUVs(ref uv4, accessors, primitive.attributes.TEXCOORD_3, vertCount);
                                ReadUVs(ref uv5, accessors, primitive.attributes.TEXCOORD_4, vertCount);
                                ReadUVs(ref uv6, accessors, primitive.attributes.TEXCOORD_5, vertCount);
                                ReadUVs(ref uv7, accessors, primitive.attributes.TEXCOORD_6, vertCount);
                                ReadUVs(ref uv8, accessors, primitive.attributes.TEXCOORD_7, vertCount);
                            }
                        }

                        bool hasTargetNames = gltfMesh.extras != null && gltfMesh.extras.targetNames != null;
                        if (hasTargetNames) {
                            if (gltfMesh.primitives.All(x => x.targets != null && x.targets.Count != gltfMesh.extras.targetNames.Length)) {
                                Debug.LogWarning("Morph target names found but don't match target array length");
                                hasTargetNames = false;
                            }
                        }

                        int finalVertCount = verts.Count;
                        for (int i = 0; i < gltfMesh.primitives.Count; i++) {
                            GLTFPrimitive primitive = gltfMesh.primitives[i];
                            if (primitive.targets != null) {
                                for (int k = 0; k < primitive.targets.Count; k++) {
                                    BlendShape blendShape = new BlendShape();
                                    blendShape.pos = GetMorphWeights(primitive.targets[k].POSITION, submeshVertexStart[i], finalVertCount, accessors);
                                    blendShape.norm = GetMorphWeights(primitive.targets[k].NORMAL, submeshVertexStart[i], finalVertCount, accessors);
                                    blendShape.tan = GetMorphWeights(primitive.targets[k].TANGENT, submeshVertexStart[i], finalVertCount, accessors);
                                    if (hasTargetNames) blendShape.name = gltfMesh.extras.targetNames[k];
                                    else blendShape.name = "morph-" + blendShapes.Count;
                                    blendShapes.Add(blendShape);
                                }
                            }
                        }
                    }
                }

                Vector3[] GetMorphWeights(int? accessor, int vertStartIndex, int vertCount, GLTFAccessor.ImportResult[] accessors) {
                    if (accessor.HasValue) {
                        if (accessors[accessor.Value] == null) {
                            Debug.LogWarning("Accessor is null");
                            return new Vector3[vertCount];
                        }
                        Vector3[] accessorData = accessors[accessor.Value].ReadVec3(true)
                            .Select(v => { v.x = -v.x; return v; }).ToArray();
                        if (accessorData.Length != vertCount) {
                            Vector3[] resized = new Vector3[vertCount];
                            Array.Copy(accessorData, 0, resized, vertStartIndex, accessorData.Length);
                            return resized;
                        }
                        return accessorData;
                    } else {
                        return new Vector3[vertCount];
                    }
                }

                public Mesh ToMesh() {
                    Mesh mesh = new Mesh();
                    if (verts.Count >= ushort.MaxValue)
                        mesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
                    mesh.vertices = verts.ToArray();
                    mesh.subMeshCount = submeshTris.Count;
                    var onlyTriangles = true;
                    for (int i = 0; i < submeshTris.Count; i++) {
                        switch (submeshTrisMode[i]) {
                            case RenderingMode.POINTS:
                                mesh.SetIndices(submeshTris[i].ToArray(), MeshTopology.Points, i);
                                onlyTriangles = false;
                                break;
                            case RenderingMode.LINES:
                                mesh.SetIndices(submeshTris[i].ToArray(), MeshTopology.Lines, i);
                                onlyTriangles = false;
                                break;
                            case RenderingMode.LINE_STRIP:
                                mesh.SetIndices(submeshTris[i].ToArray(), MeshTopology.LineStrip, i);
                                onlyTriangles = false;
                                break;
                            case RenderingMode.TRIANGLES:
                                mesh.SetTriangles(submeshTris[i].ToArray(), i);
                                break;
                            default:
                                Debug.LogWarning("GLTF rendering mode " + submeshTrisMode[i] + " not supported.");
                                return null;
                        }
                    }

                    mesh.colors = colors.ToArray();
                    if (uv1 != null) mesh.uv = uv1.ToArray();
                    if (uv2 != null) mesh.uv2 = uv2.ToArray();
                    if (uv3 != null) mesh.uv3 = uv3.ToArray();
                    if (uv4 != null) mesh.uv4 = uv4.ToArray();
                    if (uv5 != null) mesh.uv5 = uv5.ToArray();
                    if (uv6 != null) mesh.uv6 = uv6.ToArray();
                    if (uv7 != null) mesh.uv7 = uv7.ToArray();
                    if (uv8 != null) mesh.uv8 = uv8.ToArray();
                    if (weights != null) mesh.boneWeights = weights.ToArray();

                    mesh.RecalculateBounds();

                    for (int i = 0; i < blendShapes.Count; i++) {
                        mesh.AddBlendShapeFrame(blendShapes[i].name, 1f, blendShapes[i].pos, blendShapes[i].norm, blendShapes[i].tan);
                    }

                    if (normals.Count == 0 && onlyTriangles)
                        mesh.RecalculateNormals();
                    else
                        mesh.normals = normals.ToArray();

                    if (tangents.Count == 0 && onlyTriangles)
                        mesh.RecalculateTangents();
                    else
                        mesh.tangents = tangents.ToArray();

                    mesh.name = name;
                    return mesh;
                }

                public void NormalizeWeights(ref Vector4 weights) {
                    float total = weights.x + weights.y + weights.z + weights.w;
                    float mult = 1f / total;
                    weights.x *= mult;
                    weights.y *= mult;
                    weights.z *= mult;
                    weights.w *= mult;
                }

                public void ReadUVs(ref List<Vector2> uvs, GLTFAccessor.ImportResult[] accessors, int? texcoord, int vertCount) {
                    if (!texcoord.HasValue) {
                        if (uvs != null)
                            uvs.AddRange(new Vector2[vertCount - uvs.Count]);
                        return;
                    }
                    Vector2[] _uvs = accessors[texcoord.Value].ReadVec2(true);
                    for (int i = 0; i < _uvs.Length; i++)
                        _uvs[i].y = 1 - _uvs[i].y;
                    if (uvs == null)
                        uvs = new List<Vector2>(_uvs);
                    else
                        uvs.AddRange(_uvs);
                }
            }

            MeshData[] meshData;
            List<GLTFMesh> meshes;
            GLTFMaterial.ImportTask materialTask;

            public ImportTask(List<GLTFMesh> meshes, GLTFAccessor.ImportTask accessorTask, GLTFBufferView.ImportTask bufferViewTask, GLTFMaterial.ImportTask materialTask, ImportSettings importSettings) : base(accessorTask, materialTask) {
                this.meshes = meshes;
                this.materialTask = materialTask;

                task = new Task(() => {
                    if (meshes == null) return;

                    meshData = new MeshData[meshes.Count];
                    for (int i = 0; i < meshData.Length; i++)
                        meshData[i] = new MeshData(meshes[i], accessorTask.result, bufferViewTask.result);
                });
            }

            public override IEnumerator TaskCoroutine(Action<float> onProgress = null) {
                if (meshData == null) {
                    if (onProgress != null)
                        onProgress(1f);
                    IsCompleted = true;
                    yield break;
                }

                result = new ImportResult[meshData.Length];
                for (int i = 0; i < meshData.Length; i++) {
                    if (meshData[i] == null) {
                        Debug.LogWarning(string.Format("Mesh {0} import error", i));
                        continue;
                    }

                    result[i] = new ImportResult();
                    result[i].mesh = meshData[i].ToMesh();
                    result[i].materials = new Material[meshes[i].primitives.Count];
                    for (int k = 0; k < meshes[i].primitives.Count; k++) {
                        int? matIndex = meshes[i].primitives[k].material;
                        if (matIndex.HasValue && materialTask.result != null && materialTask.result.Count() > matIndex.Value) {
                            GLTFMaterial.ImportResult matImport = materialTask.result[matIndex.Value];
                            if (matImport != null) {
                                result[i].materials[k] = matImport.material;
                            } else {
                                Debug.LogWarning(string.Format("Mesh[{0}].matIndex points to null material", i));
                                result[i].materials[k] = GLTFMaterial.defaultMaterial;
                            }
                        } else {
                            result[i].materials[k] = GLTFMaterial.defaultMaterial;
                        }
                    }

                    if (string.IsNullOrEmpty(result[i].mesh.name))
                        result[i].mesh.name = "mesh" + i;
                    onProgress?.Invoke((float)(i + 1) / (float)meshData.Length);
                }
                IsCompleted = true;
            }
        }

        public class ExportResult : GLTFMesh {
            [JsonIgnore] public GLTFNode.ExportResult node;
            [JsonIgnore] public Mesh mesh;
            [JsonIgnore] public int index;
        }

        public static List<ExportResult> Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes, ref byte[] bufferData) {
            Dictionary<Mesh, ExportResult> results = new Dictionary<Mesh, ExportResult>();
            for (int i = 0; i < nodes.Count; i++) {
                if (nodes[i].filter) {
                    Mesh mesh = nodes[i].filter.sharedMesh;
                    if (mesh != null) {
                        bool writeTangents = nodes[i].renderer != null && nodes[i].renderer.sharedMaterial != null
                            && nodes[i].renderer.sharedMaterial.IsKeywordEnabled("_NORMALMAP");
                        ExportResult result;
                        if (!results.TryGetValue(mesh, out result)) {
                            result = Export(gltfObject, mesh, ref bufferData, writeTangents);
                            result.node = nodes[i];
                            result.index = results.Count;
                            results.Add(mesh, result);
                        }
                        nodes[i].mesh = result.index;
                    }
                }
                if (nodes[i].meshCollider) {
                    Mesh mesh = nodes[i].meshCollider.sharedMesh;
                    if (mesh != null) {
                        nodes[i].mesh = results.Count;
                        ExportResult result;
                        if (!results.TryGetValue(mesh, out result)) {
                            result = Export(gltfObject, mesh, ref bufferData);
                            result.node = nodes[i];
                            result.index = results.Count;
                            results.Add(mesh, result);
                        }
                        nodes[i].mesh = result.index;
                    }
                }
            }
            List<GLTFMesh.ExportResult> meshes = results.Values.OrderBy(x => x.index).ToList();
            gltfObject.meshes = meshes.Cast<GLTFMesh>().ToList();
            return meshes;
        }

        public static ExportResult Export(GLTFObject gltfObject, Mesh mesh, ref byte[] bufferData, bool writeTangents = false) {
            ExportResult result = new ExportResult();
            result.name = mesh.name;
            result.mesh = mesh;
            result.primitives = new List<GLTFPrimitive>();
            for (int i = 0; i < mesh.subMeshCount; i++) {
                GLTFPrimitive primitive = new GLTFPrimitive();
                GLTFPrimitive.GLTFAttributes attributes = new GLTFPrimitive.GLTFAttributes();

                SubMeshDescriptor submesh = mesh.GetSubMesh(i);

                Vector3[] vertices = mesh.vertices.Skip(submesh.firstVertex).Take(submesh.vertexCount)
                    .Select(v => { v.x = -v.x; return v; }).ToArray();
                attributes.POSITION = Exporter.WriteVec3(vertices, gltfObject, ref bufferData);

                Vector3[] normals = mesh.normals.Skip(submesh.firstVertex).Take(submesh.vertexCount)
                    .Select(v => { v.x = -v.x; return v; }).ToArray();
                attributes.NORMAL = Exporter.WriteVec3(normals, gltfObject, ref bufferData);

                if (writeTangents) {
                    Vector4[] tangents = mesh.tangents.Skip(submesh.firstVertex).Take(submesh.vertexCount)
                        .Select(v => { v.y = -v.y; v.z = -v.z; return v; }).ToArray();
                    attributes.TANGENT = Exporter.WriteVec4(tangents, gltfObject, ref bufferData);
                }

                int[] triangles = mesh.GetTriangles(i).Reverse().Select(x => x - submesh.firstVertex).ToArray();
                primitive.indices = Exporter.WriteInt(triangles, gltfObject, ref bufferData, BufferViewTarget.ELEMENT_ARRAY_BUFFER);

                if (mesh.uv.Length > 0) {
                    Vector2[] uvs = mesh.uv.Skip(submesh.firstVertex).Take(submesh.vertexCount)
                        .Select(v => { v.y = 1 - v.y; return v; }).ToArray();
                    attributes.TEXCOORD_0 = Exporter.WriteVec2(uvs, gltfObject, ref bufferData);
                }

                primitive.attributes = attributes;
                result.primitives.Add(primitive);
            }
            return result;
        }
    }
}