// adapted from https://github.com/Siccity/GLTFUtility/blob/3d5d97d7e174bde3c5e58b6f02301de36f7f6eb7/Scripts/Spec/GLTFSkin.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System.Threading.Tasks;

namespace Simulate.GLTF {
    public class GLTFSkin {
        public int? inverseBindMatrices;
        public int[] joints;
        public int? skeleton;
        public string name;

        public class ImportResult {
            public Matrix4x4[] inverseBindMatrices;
            public int[] joints;

            public SkinnedMeshRenderer SetupSkinnedMeshRenderer(GameObject gameObject, Mesh mesh, GLTFNode.ImportResult[] nodes) {
                SkinnedMeshRenderer skinnedMeshRenderer = gameObject.AddComponent<SkinnedMeshRenderer>();
                Transform[] bones = new Transform[joints.Length];
                for (int i = 0; i < bones.Length; i++) {
                    int jointNodeIndex = joints[i];
                    GLTFNode.ImportResult jointNode = nodes[jointNodeIndex];
                    bones[i] = jointNode.transform;
                    if (string.IsNullOrEmpty(jointNode.transform.name))
                        jointNode.transform.name = "joint" + i;
                }
                skinnedMeshRenderer.bones = bones;
                skinnedMeshRenderer.rootBone = bones[0];

                if (inverseBindMatrices != null) {
                    if (inverseBindMatrices.Length != joints.Length)
                        Debug.LogWarning("InverseBindMatrices count and joints count mismatch");
                    Matrix4x4 m = nodes[0].transform.localToWorldMatrix;
                    Matrix4x4[] bindPoses = new Matrix4x4[joints.Length];
                    for (int i = 0; i < joints.Length; i++)
                        bindPoses[i] = inverseBindMatrices[i];
                    mesh.bindposes = bindPoses;
                } else {
                    Matrix4x4 m = nodes[0].transform.localToWorldMatrix;
                    Matrix4x4[] bindPoses = new Matrix4x4[joints.Length];
                    for (int i = 0; i < joints.Length; i++)
                        bindPoses[i] = nodes[joints[i]].transform.worldToLocalMatrix * m;
                    mesh.bindposes = bindPoses;
                }
                skinnedMeshRenderer.sharedMesh = mesh;
                return skinnedMeshRenderer;
            }
        }

        public ImportResult Import(GLTFAccessor.ImportResult[] accessors) {
            ImportResult result = new ImportResult();
            result.joints = joints;
            if (inverseBindMatrices.HasValue) {
                result.inverseBindMatrices = accessors[inverseBindMatrices.Value].ReadMatrix4x4();
                for (int i = 0; i < result.inverseBindMatrices.Length; i++) {
                    Matrix4x4 m = result.inverseBindMatrices[i];
                    Vector4 row0 = m.GetRow(0);
                    row0.y = -row0.y;
                    row0.z = -row0.z;
                    Vector4 row1 = m.GetRow(1);
                    row1.x = -row1.x;
                    Vector4 row2 = m.GetRow(2);
                    row2.x = -row2.x;
                    Vector4 row3 = m.GetRow(3);
                    row3.x = -row3.x;
                    m.SetColumn(0, row0);
                    m.SetColumn(1, row1);
                    m.SetColumn(2, row2);
                    m.SetColumn(3, row3);
                    result.inverseBindMatrices[i] = m;
                }
            }
            return result;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            public ImportTask(List<GLTFSkin> skins, GLTFAccessor.ImportTask accessorTask) : base(accessorTask) {
                task = new Task(() => {
                    if (skins == null) return;
                    result = new ImportResult[skins.Count];
                    for (int i = 0; i < result.Length; i++)
                        result[i] = skins[i].Import(accessorTask.result);
                });
            }
        }
    }
}