using UnityEngine;
using UnityEngine.Events;
using System.Collections;

namespace SimEnv {

    public interface ISensor {

        public string GetName();
        public int getSize();
        public int[] getShape();
        public IEnumerator getObs(uint[] buffer, int index);
    }
}