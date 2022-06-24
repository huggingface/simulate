using System.Collections.Generic;

namespace SimEnv.Agents {
    public class HFRlAgent : IGLTFExtension {
        //public string name = "";
        public float[] color;
        public float height = 1f;
        public float move_speed = 1f;
        public float turn_speed = 1f;
        public string action_name = "";
        public string action_dist = "";

        public List<string> available_actions = new List<string>();

        // reward function definitions
        public List<string> reward_functions = new List<string>();
        public List<string> reward_entity1s = new List<string>();
        public List<string> reward_entity2s = new List<string>();
        public List<string> reward_distance_metrics = new List<string>();
        public List<float> reward_scalars = new List<float>();
        public List<float> reward_thresholds = new List<float>();
        public List<bool> reward_is_terminals = new List<bool>();
        public List<bool> reward_is_collectables = new List<bool>();

        public void Initialize(Node node) {
            new Agent(node, this);
        }
    }
}