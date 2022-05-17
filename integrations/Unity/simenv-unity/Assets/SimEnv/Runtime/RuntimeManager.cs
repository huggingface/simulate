using UnityEngine;
using SimEnv.GLTF;
using System.Collections.Generic;

namespace SimEnv {
    [CreateAssetMenu(fileName = "RuntimeManager", menuName = "SimEnv/Runtime Manager")]
    public class RuntimeManager : SingletonScriptableObject<RuntimeManager> {
        static int frameRate = 30;
        const int FRAME_SKIP = 4;
        static float frameInterval => 1f / frameRate;
        GameObject root = null;
        GameObject agent = null;
        Agent agentScript = null;
        public void BuildSceneFromBytes(byte[] bytes) {
            Physics.autoSimulation = false;
            root = Importer.LoadFromBytes(bytes);
            Debug.Log("environment built");
            agent = GameObject.FindWithTag("Agent");

            if (agent) {
                Debug.Log("found agent");
                agentScript = agent.GetComponent<Agent>();
            }

        }
        public void Step(List<float> action) {

            // find the agent
            if (agentScript) {
                Debug.Log("stepping agent");
                agentScript.SetAction(action);
            } else {
                Debug.Log("Warning, attempting to step environment with an agent");
            }
            for (int i = 0; i < FRAME_SKIP; i++) {
                Physics.Simulate(frameInterval);
            }

            // TODO: send back the observation to python side
        }
    }
}