// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/Spec/GLTFScene.cs
using System.Collections.Generic;

namespace Simulate.GLTF {
    public class GLTFScene {
        public string name;
        public List<int> nodes;

        public static GLTFScene Export(GLTFObject gltfObject, List<GLTFNode.ExportResult> nodes) {
            GLTFScene scene = new GLTFScene();
            scene.nodes = new List<int>();
            for (int i = 0; i < nodes.Count; i++) {
                if (nodes[i].transform.parent == null)
                    scene.nodes.Add(i);
            }
            gltfObject.scenes = new List<GLTFScene>() { scene };
            return scene;
        }
    }
}