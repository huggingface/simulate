using Newtonsoft.Json;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;

namespace Simulate.GLTF {
    public class HFPhysicMaterials {
        public List<GLTFPhysicMaterial> objects;

        public HFPhysicMaterials() {
            objects = new List<GLTFPhysicMaterial>();
        }

        public class GLTFPhysicMaterial {
            public string name = "";
            public float dynamic_friction = .6f;
            public float static_friction = .6f;
            public float bounciness = 0f;
            [JsonConverter(typeof(EnumConverter))] public PhysicMaterialCombine friction_combine;
            [JsonConverter(typeof(EnumConverter))] public PhysicMaterialCombine bounce_combine;

            public bool ShouldSerializedynamicFriction() => dynamic_friction != .6f;
            public bool ShouldSerializestaticFriction() => static_friction != .6f;
            public bool ShouldSerializebounciness() => bounciness != 0;
            public bool ShouldSerializefrictionCombine() => friction_combine != PhysicMaterialCombine.average;
            public bool ShouldSerializebounceCombine() => bounce_combine != PhysicMaterialCombine.average;

            public override int GetHashCode() {
                return name.GetHashCode()
                    ^ dynamic_friction.GetHashCode()
                    ^ static_friction.GetHashCode()
                    ^ bounciness.GetHashCode()
                    ^ friction_combine.GetHashCode()
                    ^ bounce_combine.GetHashCode();
            }

            public override bool Equals(object obj) {
                if (!(obj is GLTFPhysicMaterial)) return false;
                GLTFPhysicMaterial other = obj as GLTFPhysicMaterial;
                if (name == other.name
                    && dynamic_friction == other.dynamic_friction
                    && static_friction == other.static_friction
                    && bounciness == other.bounciness
                    && friction_combine == other.friction_combine
                    && bounce_combine == other.bounce_combine)
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
                    dynamicFriction = physicMaterial.dynamic_friction,
                    staticFriction = physicMaterial.static_friction,
                    bounciness = physicMaterial.bounciness,
                    frictionCombine = (UnityEngine.PhysicMaterialCombine)((int)physicMaterial.friction_combine),
                    bounceCombine = (UnityEngine.PhysicMaterialCombine)((int)physicMaterial.bounce_combine),
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
                collider.physic_material = objects.IndexOf(physicMaterial);
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
                dynamic_friction = material.dynamicFriction,
                static_friction = material.staticFriction,
                bounciness = material.bounciness,
                friction_combine = (PhysicMaterialCombine)((int)material.frictionCombine),
                bounce_combine = (PhysicMaterialCombine)((int)material.bounceCombine),
            };
            return physicMaterial;
        }
    }
}
