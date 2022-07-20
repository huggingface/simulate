using UnityEngine;
using UnityEngine.Events;
using System.Collections;

namespace SimEnv {

    public interface ISensor {
        public int getSize();
        public int[] getShape();
        public IEnumerator getObs(UnityAction<Color32[]> callback);
    }
}