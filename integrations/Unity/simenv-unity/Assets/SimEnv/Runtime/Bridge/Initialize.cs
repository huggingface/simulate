using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace SimEnv {
    public class Initialize : ICommand {
        public string b64bytes;
        public int frame_rate = 30;
        public int frame_skip = 1;
        public bool return_nodes = true;
        public bool return_frames = true;
        public List<string> node_filter;
        public List<string> camera_filter;

        public void Execute(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            ExecuteAsync(kwargs, callback);
        }

        async void ExecuteAsync(Dictionary<string, object> kwargs, UnityAction<string> callback) {
            try {
                await Simulator.Initialize(b64bytes, kwargs);
                MetaData.returnNodes = return_nodes;
                MetaData.returnFrames = return_frames;
                MetaData.frameRate = frame_rate;
                MetaData.frameSkip = frame_skip;
                MetaData.nodeFilter = node_filter;
                MetaData.cameraFilter = camera_filter;
            } catch (System.Exception e) {
                string error = "Failed to build scene from GLTF: " + e.ToString();
                Debug.LogWarning(error);
                callback(error);
                return;
            }
            callback("ack");
        }
    }
}