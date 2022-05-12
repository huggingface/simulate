// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFImage.cs
using UnityEngine;
using System.Collections;
using System;
using UnityEngine.Networking;
using System.IO;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;

namespace SimEnv.GLTF {
    public class GLTFImage {
        public string uri;
        public string mimeType;
        public int? bufferView;
        public string name;

        public class ImportResult {
            public byte[] bytes;
            public string path;

            public ImportResult(byte[] bytes, string path = null) {
                this.bytes = bytes;
                this.path = path;
            }

            public IEnumerator CreateTextureAsync(bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
                if(!string.IsNullOrEmpty(path)) {
#if UNITY_EDITOR
                    Texture2D assetTexture = UnityEditor.AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                    if(assetTexture != null) {
                        onFinish(assetTexture);
                        if(onProgress != null)
                            onProgress(1f);
                        yield break;
                    }
#endif
                    path = "File://" + path;
                    using(UnityWebRequest uwr = UnityWebRequestTexture.GetTexture(path, true)) {
                        UnityWebRequestAsyncOperation operation = uwr.SendWebRequest();
                        float progress = 0;
                        while(!operation.isDone) {
                            if(progress != uwr.downloadProgress && onProgress != null)
                                onProgress(uwr.downloadProgress);
                            yield return null;
                        }
                        if(onProgress != null)
                            onProgress(1f);
                        if(uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocolError) {
                            Debug.LogError(string.Format("GLTFImage to texture error: {0}", uwr.error));
                        } else {
                            Texture2D tex = DownloadHandlerTexture.GetContent(uwr);
                            tex.name = Path.GetFileNameWithoutExtension(path);
                            onFinish(tex);
                        }
                        uwr.Dispose();
                    }
                } else {
                    Texture2D tex = new Texture2D(2, 2, TextureFormat.ARGB32, true, linear);
                    if(!tex.LoadImage(bytes)) {
                        Debug.LogError("mimeType not supported");
                        yield break;
                    }
                    onFinish(tex);
                }
            }

        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            public ImportTask(List<GLTFImage> images, string directoryRoot, GLTFBufferView.ImportTask bufferViewTask) : base(bufferViewTask) {
                task = new Task(() => {
                    if(images == null) return;
                    result = new ImportResult[images.Count];
                    for(int i = 0; i < images.Count; i++) {
                        string fullUri = directoryRoot + images[i].uri;
                        if(!string.IsNullOrEmpty(images[i].uri)) {
                            if(File.Exists(fullUri)) {
                                byte[] bytes = File.ReadAllBytes(fullUri);
                                result[i] = new ImportResult(bytes, fullUri);
                            } else {
                                string content = images[i].uri.Split(',').Last();
                                byte[] imageBytes = Convert.FromBase64String(content);
                                result[i] = new ImportResult(imageBytes);
                            }
                        } else if(images[i].bufferView.HasValue && !string.IsNullOrEmpty(images[i].mimeType)) {
                            GLTFBufferView.ImportResult view = bufferViewTask.result[images[i].bufferView.Value];
                            byte[] bytes = new byte[view.byteLength];
                            view.stream.Position = view.byteOffset;
                            view.stream.Read(bytes, 0, view.byteLength);
                            result[i] = new ImportResult(bytes);
                        } else {
                            Debug.LogWarning("Couldn't find texture at " + fullUri);
                        }
                    }
                });
            }
        }
    }
}