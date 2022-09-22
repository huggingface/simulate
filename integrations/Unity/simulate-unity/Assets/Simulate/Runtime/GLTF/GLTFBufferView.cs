// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFBufferView.cs
using System.Collections.Generic;
using Newtonsoft.Json;
using System.IO;
using System.Threading.Tasks;

namespace Simulate.GLTF {
    public class GLTFBufferView {
        [JsonProperty(Required = Required.Always)] public int buffer;
        [JsonProperty(Required = Required.Always)] public int byteLength;
        public int byteOffset = 0;
        public int? byteStride;
        public int? target;
        public string name;

        public class ImportResult {
            public Stream stream;
            public int byteOffset;
            public int byteLength;
            public int? byteStride;
        }

        public class ImportTask : Importer.ImportTask<ImportResult[]> {
            public ImportTask(List<GLTFBufferView> bufferViews, GLTFBuffer.ImportTask bufferTask) : base(bufferTask) {
                task = new Task(() => {
                    result = new ImportResult[bufferViews.Count];
                    for (int i = 0; i < result.Length; i++) {
                        GLTFBuffer.ImportResult buffer = bufferTask.result[bufferViews[i].buffer];
                        ImportResult result = new ImportResult();
                        result.stream = buffer.stream;
                        result.byteOffset = bufferViews[i].byteOffset;
                        result.byteOffset += (int)buffer.startOffset;
                        result.byteLength = bufferViews[i].byteLength;
                        result.byteStride = bufferViews[i].byteStride;
                        this.result[i] = result;
                    }
                });
            }
        }
    }
}