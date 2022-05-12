using UnityEngine;

[CreateAssetMenu(fileName = "SimEnv", menuName = "SimEnv/Controller")]
public class SimEnv : SingletonScriptableObject<SimEnv>
{
    public static void BuildSceneFromBytes(byte[] bytes) {
        GameObject root = Importer.LoadFromBytes(bytes);
    }

#region DEPRECATED
    /* public static event UnityAction OnStep;

    static List<SimNode> _nodes;
    static List<SimNode> nodes {
        get {
            if(_nodes == null)
                _nodes = new List<SimNode>();
            return _nodes;
        }
    }

    static List<SimCamera> _cameras;
    static List<SimCamera> cameras {
        get {
            if(_cameras == null)
                _cameras = new List<SimCamera>();
            return _cameras;
        }
    }

    static int startFrame;
    static int endFrame;
    static int frameRate;
    static float frameInterval => 1f / frameRate;
    public static float FrameInterval => frameInterval;

    static int currentFrameIdx;

    public static void Initialize(int startFrame, int endFrame, int frameRate) {
        Physics.autoSimulation = false;
        SimEnv.startFrame = startFrame;
        SimEnv.endFrame = endFrame;
        SimEnv.frameRate = frameRate;
        currentFrameIdx = startFrame;
        nodes.Clear();
    }

    public static void Register(SimNode node) {
        Debug.Assert(!nodes.Contains(node));
        nodes.Add(node);
        if(node is SimCamera)
            cameras.Add((SimCamera)node);
        node.OnDeinitialize += Unregister;
    }

    public static void Unregister(SimNode node) {
        node.OnDeinitialize -= Unregister;
        Debug.Assert(nodes.Contains(node));
        nodes.Remove(node);
        if(node is SimCamera)
            cameras.Remove((SimCamera)node);
    }

    public static void Step() {
        Physics.Simulate(frameInterval);
        nodes.ForEach(node => {
            node.Record(currentFrameIdx);
        });
        OnStep?.Invoke();
        currentFrameIdx++;
    }

    public static void SetStep(int idx) {
        nodes.ForEach(node => {
            node.SetKeyframe(idx);
        });
    }

    public static void Run(UnityAction callback) {
        Client.Instance.StartCoroutine(Instance.RunCoroutine(callback));
    }

    IEnumerator RunCoroutine(UnityAction callback) {
        while(currentFrameIdx <= endFrame) {
            Step();
            yield return null;
        }
        Debug.Log("Finished simulating");
        if(callback != null)
            callback();
    }

    public static void Render(string dirpath, UnityAction callback) {
        Client.Instance.StartCoroutine(Instance.RenderCoroutine(dirpath, callback));
    }

    IEnumerator RenderCoroutine(string dirpath, UnityAction callback) {
        for(int idx = startFrame; idx <= endFrame; idx++) {
            SetStep(idx);
            yield return new WaitForEndOfFrame();
            cameras.ForEach(camera => {
                string cameraDir = Path.Combine(dirpath, camera.Name);
                if(!Directory.Exists(cameraDir))
                    Directory.CreateDirectory(cameraDir);
                string filepath = Path.Combine(cameraDir, string.Format("{0}.png", idx.ToString("D4")));
                Render(filepath, camera);
            });            
            yield return null;
        }
        Debug.Log("Finished rendering");
        if(callback != null)
            callback();
    }

    static void Render(string filepath, SimCamera simCam) {
        Camera cam = simCam.Camera;
        RenderTexture activeRenderTexture = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
        cam.Render();
        int width = simCam.Width;
        int height = simCam.Height;
        Texture2D image = new Texture2D(width, height);
        image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        image.Apply();
        RenderTexture.active = activeRenderTexture;
        byte[] bytes = image.EncodeToPNG();
        File.WriteAllBytes(filepath, bytes);
    } */
#endregion
}