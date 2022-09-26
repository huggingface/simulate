// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFImage.cs
using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace Simulate.GLTF {
    public class GLTFImage {
        public string uri;
        public string mimeType;
        public int? bufferView;
        public string name;

        public class ExportResult : GLTFImage {
            [JsonIgnore] public byte[] bytes;
            [JsonIgnore] public string path;
            [JsonIgnore] public int index;
        }

        public class ImportResult {
            public byte[] bytes;
            public string path;

            public ImportResult(byte[] bytes, string path = null) {
                this.bytes = bytes;
                this.path = path;
            }

            public IEnumerator CreateTextureAsync(bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
                if (!string.IsNullOrEmpty(path)) {
                    if (File.Exists(path)) {
                        byte[] data = File.ReadAllBytes(path);
                        Texture2D tex = new Texture2D(2, 2, TextureFormat.ARGB32, true);
                        tex.LoadImage(data);
                        tex.name = Path.GetFileNameWithoutExtension(path);
                        onFinish(tex);
                    } else {
                        Debug.LogError("File not found at path: " + path);
                        yield break;
                    }
                } else {
                    Texture2D tex = new Texture2D(2, 2, TextureFormat.ARGB32, true, linear);
                    if (!tex.LoadImage(bytes)) {
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
                    if (images == null) return;
                    result = new ImportResult[images.Count];
                    for (int i = 0; i < images.Count; i++) {
                        string fullUri = directoryRoot + images[i].uri;
                        if (!string.IsNullOrEmpty(images[i].uri)) {
                            if (File.Exists(fullUri)) {
                                byte[] bytes = File.ReadAllBytes(fullUri);
                                result[i] = new ImportResult(bytes, fullUri);
                            } else {
                                string content = images[i].uri.Split(',').Last();
                                byte[] imageBytes = Convert.FromBase64String(content);
                                result[i] = new ImportResult(imageBytes);
                            }
                        } else if (images[i].bufferView.HasValue && !string.IsNullOrEmpty(images[i].mimeType)) {
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

        public static List<GLTFImage.ExportResult> Export(GLTFObject gltfObject, Dictionary<string, ExportResult> images, bool embedded) {
            if (images.Count > 0) {
                gltfObject.textures = new List<GLTFTexture>();
                gltfObject.images = new List<GLTFImage>();
            }
            images.Keys.OrderBy(x => images[x].index).ToList().ForEach(uri => {
                GLTFImage.ExportResult image = images[uri];
                if (embedded) {
                    string bytestring = Convert.ToBase64String(image.bytes);
                    image.uri = "data:image/png;base64," + bytestring;
                } else {
                    File.WriteAllBytes(image.path, image.bytes);
                }
                GLTFTexture texture = new GLTFTexture();
                texture.source = image.index;
                texture.name = image.name;
                gltfObject.textures.Add(texture);
                gltfObject.images.Add((GLTFImage)image);
            });
            return images.Values.ToList();
        }
    }
}