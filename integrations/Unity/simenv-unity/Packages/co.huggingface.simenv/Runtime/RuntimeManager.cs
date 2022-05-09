using UnityEngine;
using SimEnv.GLTF;

namespace SimEnv {
    [CreateAssetMenu(fileName = "RuntimeManager", menuName = "SimEnv/Runtime Manager")]
    public class RuntimeManager : SingletonScriptableObject<RuntimeManager> {
        public static void BuildSceneFromBytes(byte[] bytes) {
            GameObject root = Importer.LoadFromBytes(bytes);
        }
    }
}