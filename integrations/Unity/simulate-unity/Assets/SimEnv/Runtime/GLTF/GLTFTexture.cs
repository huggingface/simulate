// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFTexture.cs
using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.IO;

namespace Simulate.GLTF {
    public class GLTFTexture {
        public int? sampler;
        public int? source;
        public string name;

        public class ImportResult {
            GLTFImage.ImportResult image;
            Texture2D cache;

            public ImportResult(GLTFImage.ImportResult image) {
                this.image = image;
            }

            public IEnumerator GetTextureCached(bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
                if (cache == null) {
                    IEnumerator coroutine = image.CreateTextureAsync(linear, x => cache = x, onProgress);
                    while (coroutine.MoveNext())
                        yield return null;
                }
                onFinish(cache);
            }
        }

        public ImportResult Import(GLTFImage.ImportResult[] images) {
            if (source.HasValue)
                return new ImportResult(images[source.Value]);
            return null;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            public ImportTask(List<GLTFTexture> textures, GLTFImage.ImportTask imageTask) : base(imageTask) {
                task = new Task(() => {
                    if (textures == null) return;
                    result = new ImportResult[textures.Count];
                    for (int i = 0; i < result.Length; i++)
                        result[i] = textures[i].Import(imageTask.result);
                });
            }
        }

        public static GLTFMaterial.TextureInfo Export(Texture2D texture, Dictionary<string, GLTFImage.ExportResult> images, string filepath) {
            string uri = texture.name + ".png";
            if (!images.TryGetValue(uri, out GLTFImage.ExportResult image)) {
                image = new GLTFImage.ExportResult();
                image.name = texture.name;
                image.uri = uri;
                image.path = string.Format("{0}/{1}", Path.GetDirectoryName(filepath), uri);
                image.bytes = texture.Decompress().EncodeToPNG();
                image.index = images.Count;
                images.Add(uri, image);
            }
            return new GLTFMaterial.TextureInfo() { index = image.index };
        }
    }
}