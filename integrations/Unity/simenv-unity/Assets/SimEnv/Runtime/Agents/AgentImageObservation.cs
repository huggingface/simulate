using ISimEnv;
using UnityEngine;

namespace SimEnv {
    public class AgentImageObservation : IAgentObservation {
        public uint[] pixels;

        public AgentImageObservation(Color32[] colors) {
            pixels = new uint[colors.Length * 3];
            for(int i = 0; i < colors.Length; i++) {
                pixels[i * 3] = colors[i].r;
                pixels[i * 3 + 1] = colors[i].g;
                pixels[i * 3 + 2] = colors[i].b;
            }
        }

        public AgentImageObservation(uint[] pixels) {
            this.pixels = pixels;
        }
    }
}