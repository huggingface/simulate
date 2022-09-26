// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Importer.cs
using System.Collections;
using System.Threading.Tasks;
using System.Linq;
using System;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Text;

namespace Simulate.GLTF {
    public static class Importer {
        public abstract class ImportTask {
            public Task task;
            public ImportTask[] waitFor;
            public bool IsReady => waitFor.All(x => x.IsCompleted);
            public bool IsCompleted { get; protected set; }

            public ImportTask(params ImportTask[] waitFor) {
                this.waitFor = waitFor;
                IsCompleted = false;
            }

            public virtual IEnumerator TaskCoroutine(Action<float> onProgress = null) {
                IsCompleted = true;
                yield break;
            }
        }

        public abstract class ImportTask<T> : ImportTask {
            public T result;

            public ImportTask(params ImportTask[] waitFor) : base(waitFor) { }

            public T RunSynchronously() {
                if (task != null)
                    task.RunSynchronously();
                IEnumerator coroutine = TaskCoroutine();
                while (coroutine.MoveNext()) { };
                return result;
            }
        }

        public static GameObject LoadFromFile(string filepath, Format format = Format.AUTO) {
            AnimationClip[] animations;
            return LoadFromFile(filepath, new ImportSettings(), out animations, format);
        }

        public static GameObject LoadFromFile(string filepath, ImportSettings importSettings, Format format = Format.AUTO) {
            AnimationClip[] animations;
            return LoadFromFile(filepath, importSettings, out animations, format);
        }

        public static GameObject LoadFromFile(string filepath, ImportSettings importSettings, out AnimationClip[] animations, Format format = Format.AUTO) {
            switch (format) {
                case Format.GLB:
                    return ImportGLB(filepath, importSettings, out animations);
                case Format.GLTF:
                    return ImportGLTF(filepath, null, importSettings, out animations);
                default:
                    string extension = Path.GetExtension(filepath).ToLower();
                    if (extension == ".glb")
                        return ImportGLB(filepath, importSettings, out animations);
                    else if (extension == ".gltf")
                        return ImportGLTF(filepath, null, importSettings, out animations);
                    else {
                        Debug.LogWarning("Invalid extension " + extension);
                        animations = null;
                        return null;
                    }
            }
        }

        public static GameObject LoadFromBytes(byte[] bytes, ImportSettings importSettings = null) {
            AnimationClip[] animations;
            if (importSettings == null)
                importSettings = new ImportSettings();
            return ImportGLB(bytes, importSettings, out animations);
        }

        public static GameObject LoadFromBytes(byte[] bytes, ImportSettings importSettings, out AnimationClip[] animations) {
            return ImportGLB(bytes, importSettings, out animations);
        }

        public static async Task<GameObject> LoadFromBytesAsync(byte[] bytes, ImportSettings importSettings = null) {
            GameObject root = null;
            ImportGLBAsync(bytes, importSettings, (result, clips) => {
                root = result;
            });
            while (root == null)
                await Task.Yield();
            return root;
        }

        public static void LoadFromFileAsync(string filepath, ImportSettings importSettings, Action<GameObject, AnimationClip[]> onFinished, Action<float> onProgress = null) {
            ImportGLTFAsync(filepath, importSettings, onFinished, onProgress);
        }

        public static GameObject LoadFromJson(string json) {
            AnimationClip[] animations;
            return ImportGLTF(null, json, new ImportSettings(), out animations);
        }

        public static GameObject LoadFromJson(string json, ImportSettings importSettings) {
            AnimationClip[] animations;
            return ImportGLTF(null, json, importSettings, out animations);
        }

        public static GameObject LoadFromJson(string json, ImportSettings importSettings, out AnimationClip[] animations) {
            return ImportGLTF(null, json, importSettings, out animations);
        }

        static GameObject ImportGLB(string filepath, ImportSettings importSettings, out AnimationClip[] animations) {
            FileStream stream = File.OpenRead(filepath);
            long binChunkStart;
            string json = GetGLBJson(stream, out binChunkStart);
            GLTFObject gltfObject = JsonConvert.DeserializeObject<GLTFObject>(json);
            return gltfObject.LoadInternal(filepath, null, binChunkStart, importSettings, out animations);
        }

        static GameObject ImportGLB(byte[] bytes, ImportSettings importSettings, out AnimationClip[] animations) {
            Stream stream = new MemoryStream(bytes);
            long binChunkStart;
            string json = GetGLBJson(stream, out binChunkStart);
            GLTFObject gltfObject = JsonConvert.DeserializeObject<GLTFObject>(json);
            return gltfObject.LoadInternal(null, bytes, binChunkStart, importSettings, out animations);
        }

        public static void ImportGLBAsync(string filepath, ImportSettings importSettings, Action<GameObject, AnimationClip[]> onFinished, Action<float> onProgress = null) {
            FileStream stream = File.OpenRead(filepath);
            long binChunkStart;
            string json = GetGLBJson(stream, out binChunkStart);
            LoadAsync(json, filepath, null, binChunkStart, importSettings, onFinished, onProgress).RunCoroutine();
        }

        public static void ImportGLBAsync(byte[] bytes, ImportSettings importSettings, Action<GameObject, AnimationClip[]> onFinished, Action<float> onProgress = null) {
            Stream stream = new MemoryStream(bytes);
            long binChunkStart;
            string json = GetGLBJson(stream, out binChunkStart);
            LoadAsync(json, null, bytes, binChunkStart, importSettings, onFinished, onProgress).RunCoroutine();
        }

        static string GetGLBJson(Stream stream, out long binChunkStart) {
            byte[] buffer = new byte[12];
            stream.Read(buffer, 0, 12);
            // 12 byte header
            // 0-4 "glTF"
            // 4-8 version = 2
            // 8-12 total length
            string magic = Encoding.Default.GetString(buffer, 0, 4);
            if (magic != "glTF") {
                Debug.LogWarning("Input does not look like .glb");
                binChunkStart = 0;
                return null;
            }
            uint version = BitConverter.ToUInt32(buffer, 4);
            if (version != 2) {
                Debug.LogWarning("Unsupported gltf version: " + version);
                binChunkStart = 0;
                return null;
            }
            stream.Read(buffer, 0, 8);
            uint chunkLength = BitConverter.ToUInt32(buffer, 0);
            TextReader reader = new StreamReader(stream);
            char[] jsonChars = new char[chunkLength];
            reader.Read(jsonChars, 0, (int)chunkLength);
            string json = new string(jsonChars);
            binChunkStart = chunkLength + 20;
            stream.Close();
            return json;
        }

        static GameObject ImportGLTF(string filepath, string json, ImportSettings importSettings, out AnimationClip[] animations) {
            if (string.IsNullOrEmpty(json))
                json = File.ReadAllText(filepath);
            GLTFObject gltfObject = JsonConvert.DeserializeObject<GLTFObject>(json);
            return gltfObject.LoadInternal(filepath, null, 0, importSettings, out animations);
        }

        public static void ImportGLTFAsync(string filepath, ImportSettings importSettings, Action<GameObject, AnimationClip[]> onFinished, Action<float> onProgress = null) {
            string json = File.ReadAllText(filepath);
            LoadAsync(json, filepath, null, 0, importSettings, onFinished, onProgress).RunCoroutine();
        }

        static GameObject LoadInternal(this GLTFObject gltfObject, string filepath, byte[] bytefile, long binChunkStart, ImportSettings importSettings, out AnimationClip[] animations) {
            string directoryRoot = filepath != null ? Directory.GetParent(filepath).ToString() + "/" : null;

            GLTFBuffer.ImportTask bufferTask = new GLTFBuffer.ImportTask(gltfObject.buffers, filepath, bytefile, binChunkStart);
            bufferTask.RunSynchronously();
            GLTFBufferView.ImportTask bufferViewTask = new GLTFBufferView.ImportTask(gltfObject.bufferViews, bufferTask);
            bufferViewTask.RunSynchronously();
            GLTFAccessor.ImportTask accessorTask = new GLTFAccessor.ImportTask(gltfObject.accessors, bufferViewTask);
            accessorTask.RunSynchronously();
            GLTFImage.ImportTask imageTask = new GLTFImage.ImportTask(gltfObject.images, directoryRoot, bufferViewTask);
            imageTask.RunSynchronously();
            GLTFTexture.ImportTask textureTask = new GLTFTexture.ImportTask(gltfObject.textures, imageTask);
            textureTask.RunSynchronously();
            GLTFMaterial.ImportTask materialTask = new GLTFMaterial.ImportTask(gltfObject.materials, textureTask, importSettings);
            materialTask.RunSynchronously();
            GLTFMesh.ImportTask meshTask = new GLTFMesh.ImportTask(gltfObject.meshes, accessorTask, bufferViewTask, materialTask, importSettings);
            meshTask.RunSynchronously();
            GLTFSkin.ImportTask skinTask = new GLTFSkin.ImportTask(gltfObject.skins, accessorTask);
            skinTask.RunSynchronously();
            List<HFPhysicMaterials.GLTFPhysicMaterial> physicMaterials = null;
            if (gltfObject.extensions != null && gltfObject.extensions.HF_physic_materials != null)
                physicMaterials = gltfObject.extensions.HF_physic_materials.objects;
            HFPhysicMaterials.ImportTask physicMaterialTask = new HFPhysicMaterials.ImportTask(physicMaterials, importSettings);
            physicMaterialTask.RunSynchronously();
            GLTFNode.ImportTask nodeTask = new GLTFNode.ImportTask(gltfObject.nodes, meshTask, skinTask, physicMaterialTask, gltfObject.cameras, gltfObject.extensions);
            nodeTask.RunSynchronously();
            GLTFAnimation.ImportResult[] animationResult = gltfObject.animations.Import(accessorTask.result, nodeTask.result, importSettings);
            if (animationResult != null)
                animations = animationResult.Select(x => x.clip).ToArray();
            else
                animations = new AnimationClip[0];

            foreach (var item in bufferTask.result)
                item.Dispose();

            return nodeTask.result.GetRoot();
        }

        static IEnumerator LoadAsync(string json, string filepath, byte[] bytefile, long binChunkStart, ImportSettings importSettings, Action<GameObject, AnimationClip[]> onFinished, Action<float> onProgress = null) {
            Task<GLTFObject> deserializeTask = new Task<GLTFObject>(() => JsonConvert.DeserializeObject<GLTFObject>(json));
            deserializeTask.Start();
            while (!deserializeTask.IsCompleted) yield return null;
            GLTFObject gltfObject = deserializeTask.Result;

            string directoryRoot = filepath != null ? Directory.GetParent(filepath).ToString() + "/" : null;

            List<ImportTask> importTasks = new List<ImportTask>();

            GLTFBuffer.ImportTask bufferTask = new GLTFBuffer.ImportTask(gltfObject.buffers, filepath, bytefile, binChunkStart);
            importTasks.Add(bufferTask);
            GLTFBufferView.ImportTask bufferViewTask = new GLTFBufferView.ImportTask(gltfObject.bufferViews, bufferTask);
            importTasks.Add(bufferViewTask);
            GLTFAccessor.ImportTask accessorTask = new GLTFAccessor.ImportTask(gltfObject.accessors, bufferViewTask);
            importTasks.Add(accessorTask);
            GLTFImage.ImportTask imageTask = new GLTFImage.ImportTask(gltfObject.images, directoryRoot, bufferViewTask);
            importTasks.Add(imageTask);
            GLTFTexture.ImportTask textureTask = new GLTFTexture.ImportTask(gltfObject.textures, imageTask);
            importTasks.Add(textureTask);
            GLTFMaterial.ImportTask materialTask = new GLTFMaterial.ImportTask(gltfObject.materials, textureTask, importSettings);
            importTasks.Add(materialTask);
            GLTFMesh.ImportTask meshTask = new GLTFMesh.ImportTask(gltfObject.meshes, accessorTask, bufferViewTask, materialTask, importSettings);
            importTasks.Add(meshTask);
            GLTFSkin.ImportTask skinTask = new GLTFSkin.ImportTask(gltfObject.skins, accessorTask);
            importTasks.Add(skinTask);
            List<HFPhysicMaterials.GLTFPhysicMaterial> physicMaterials = null;
            if (gltfObject.extensions != null && gltfObject.extensions.HF_physic_materials != null)
                physicMaterials = gltfObject.extensions.HF_physic_materials.objects;
            HFPhysicMaterials.ImportTask physicMaterialTask = new HFPhysicMaterials.ImportTask(physicMaterials, importSettings);
            importTasks.Add(physicMaterialTask);
            GLTFNode.ImportTask nodeTask = new GLTFNode.ImportTask(gltfObject.nodes, meshTask, skinTask, physicMaterialTask, gltfObject.cameras, gltfObject.extensions);
            importTasks.Add(nodeTask);

            for (int i = 0; i < importTasks.Count; i++)
                TaskSupervisor(importTasks[i], onProgress).RunCoroutine();

            while (!importTasks.All(x => x.IsCompleted)) yield return null;

            GameObject root = nodeTask.result.GetRoot();

            GLTFAnimation.ImportResult[] animationResult = gltfObject.animations.Import(accessorTask.result, nodeTask.result, importSettings);
            AnimationClip[] animations = new AnimationClip[0];
            if (animationResult != null) animations = animationResult.Select(x => x.clip).ToArray();
            if (onFinished != null) onFinished(root, animations);

            foreach (var item in bufferTask.result)
                item.Dispose();
        }

        static IEnumerator TaskSupervisor(ImportTask importTask, Action<float> onProgress = null) {
            while (!importTask.IsReady) yield return null;
            yield return null;
            if (importTask.task != null) {
                importTask.task.Start();
                while (!importTask.task.IsCompleted) yield return null;
                yield return new WaitForSeconds(0.1f);
            }
            importTask.TaskCoroutine(onProgress).RunCoroutine();
            while (!importTask.IsCompleted)
                yield return null;
            yield return new WaitForSeconds(0.1f);
        }
    }
}