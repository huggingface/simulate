// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFTexture.cs
using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public class GLTFTexture
{
    public int? sampler;
    public int? source;
    public string name;

    public class ImportResult 
    {
        GLTFImage.ImportResult image;
        Texture2D cache;

        public ImportResult(GLTFImage.ImportResult image) {
            this.image = image;
        }

        public IEnumerator GetTextureCached(bool linear, Action<Texture2D> onFinish, Action<float> onProgress = null) {
            if(cache == null) {
                IEnumerator coroutine = image.CreateTextureAsync(linear, x => cache = x, onProgress);
                while(coroutine.MoveNext())
                    yield return null;
            }
            onFinish(cache);
        }
    }

    public ImportResult Import(GLTFImage.ImportResult[] images) {
        if(source.HasValue)
            return new ImportResult(images[source.Value]);
        return null;
    }
    
    public class ImportTask : Importer.ImportTask<ImportResult[]>
    {
        public ImportTask(List<GLTFTexture> textures, GLTFImage.ImportTask imageTask) : base(imageTask) {
            task = new Task(() => {
                if(textures == null) return;
                result = new ImportResult[textures.Count];
                for(int i = 0; i < result.Length; i++)
                    result[i] = textures[i].Import(imageTask.result);
            });
        }
    }
}
