using System.Collections.Generic;

namespace SimEnv {
    public abstract class Actions {
        public string name;
        public string dist;
        public List<string> available = new List<string>();
        public float forward = 0.0f;
        public float moveRight = 0.0f;
        public float turnRight = 0.0f;

        public Actions(string name, string dist, List<string> available) {
            this.name = name;
            this.dist = dist;
            this.available = available;
        }

        public abstract void SetAction(List<float> stepAction);
    }
}