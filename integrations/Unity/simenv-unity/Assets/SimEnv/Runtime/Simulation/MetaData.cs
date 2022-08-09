using System.Collections.Generic;
using UnityEngine;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/MetaData")]
    public class MetaData : Singleton<MetaData> {
        public static int port = 55000;
        public static int frameRate = 30;
        public static int frameSkip = 1;

        public static bool returnNodes = true;
        public static bool returnFrames = true;
        public static List<string> nodeFilter;
        public static List<string> cameraFilter;
    }
}