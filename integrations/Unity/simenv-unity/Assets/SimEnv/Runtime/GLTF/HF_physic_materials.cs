using Newtonsoft.Json;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;

namespace SimEnv.GLTF {
    public class HFPhysicMaterials {
        public List<GLTFPhysicMaterial> objects;

        public HFPhysicMaterials() {
            objects = new List<GLTFPhysicMaterial>();
        }

        public class GLTFPhysicMaterial {
            public string name = "";
            public float dynamicFriction = .6f;
            public float staticFriction = .6f;
            public float bounciness = 0f;
            [JsonConverter(typeof(EnumConverter))] public PhysicMaterialCombine frictionCombine;
            [JsonConverter(typeof(EnumConverter))] public PhysicMaterialCombine bounceCombine;

            public bool ShouldSerializedynamicFriction() => dynamicFriction != .6f;
            public bool ShouldSerializestaticFriction() => staticFriction != .6f;
            public bool ShouldSerializebounciness() => bounciness != 0;
            public bool ShouldSerializefrictionCombine() => frictionCombine != PhysicMaterialCombine.average;
            public bool ShouldSerializebounceCombine() => bounceCombine != PhysicMaterialCombine.average;

            public override int GetHashCode() {
                return name.GetHashCode()
                    ^ dynamicFriction.GetHashCode()
                    ^ staticFriction.GetHashCode()
                    ^ bounciness.GetHashCode()
                    ^ frictionCombine.GetHashCode()
                    ^ bounceCombine.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFPhysicMaterial)) return false;
                GLTFPhysicMaterial other = obj as GLTFPhysicMaterial;
                if (name == other.name
                    && dynamicFriction == other.dynamicFriction
                    && staticFriction == other.staticFriction
                    && bounciness == other.bounciness
                    && frictionCombine == other.frictionCombine
                    && bounceCombine == other.bounceCombine)
                    return true;
                return false;
            }
        }

        public class ImportResult {
            public PhysicMaterial material;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            List<GLTFPhysicMaterial> materials;

            public ImportTask(List<GLTFPhysicMaterial> materials, ImportSettings importSettings) : base() {
                this.materials = materials;

                task = new Task(() => {
                    if(materials == null) return;
                    result = new ImportResult[materials.Count];
                });
            }

            public override IEnumerator TaskCoroutine(Action<float> onProgress = null) {
                if(materials == null) {
                    if(onProgress != null)
                        onProgress(1f);
                    IsCompleted = true;
                    yield break;
                }
                for (int i = 0; i < materials.Count; i++) {
                    result[i] = new ImportResult() {
                        material = CreatePhysicMaterial(materials[i])
                    };
                    yield return null;
                }
                IsCompleted = true;
            }

            PhysicMaterial CreatePhysicMaterial(GLTFPhysicMaterial physicMaterial) {
                return new PhysicMaterial() {
                    name = physicMaterial.name,
                    dynamicFriction = physicMaterial.dynamicFriction,
                    staticFriction = physicMaterial.staticFriction,
                    bounciness = physicMaterial.bounciness,
                    frictionCombine = (UnityEngine.PhysicMaterialCombine)((int)physicMaterial.frictionCombine),
                    bounceCombine = (UnityEngine.PhysicMaterialCombine)((int)physicMaterial.bounceCombine),
                };
            }
        }

        public static void Export(GLTFObject gltfObject, List<HFColliders.ExportResult> colliders) {
            List<GLTFPhysicMaterial> objects = new List<GLTFPhysicMaterial>();
            foreach (HFColliders.ExportResult collider in colliders) {
                GLTFPhysicMaterial physicMaterial = Export(collider);
                if (physicMaterial == null) continue;
                if (!objects.Contains(physicMaterial))
                    objects.Add(physicMaterial);
                collider.physicMaterial = objects.IndexOf(physicMaterial);
            }
            if (objects.Count == 0) return;
            gltfObject.extensionsUsed ??= new List<string>();
            gltfObject.extensionsUsed.Add("HF_physic_materials");
            gltfObject.extensions ??= new GLTFExtensions();
            gltfObject.extensions.HF_physic_materials ??= new HFPhysicMaterials();
            gltfObject.extensions.HF_physic_materials.objects.AddRange(objects);
            gltfObject.extensions.HF_colliders.objects = colliders.Cast<HFColliders.GLTFCollider>().ToList();
        }

        static GLTFPhysicMaterial Export(HFColliders.ExportResult collider) {
            PhysicMaterial material = collider.collider.sharedMaterial;
            if (material == null) return null;
            GLTFPhysicMaterial physicMaterial = new GLTFPhysicMaterial() {
                name = material.name,
                dynamicFriction = material.dynamicFriction,
                staticFriction = material.staticFriction,
                bounciness = material.bounciness,
                frictionCombine = (PhysicMaterialCombine)((int)material.frictionCombine),
                bounceCombine = (PhysicMaterialCombine)((int)material.bounceCombine),
            };
            return physicMaterial;
        }
    }
}
