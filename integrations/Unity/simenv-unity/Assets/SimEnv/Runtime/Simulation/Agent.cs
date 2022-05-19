using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using System;
namespace SimEnv {
    public static class JsonHelper {
        public static T[] FromJson<T>(string json) {
            Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
            return wrapper.Items;
        }

        public static string ToJson<T>(T[] array) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.Items = array;
            return JsonUtility.ToJson(wrapper);
        }

        public static string ToJson<T>(T[] array, bool prettyPrint) {
            Wrapper<T> wrapper = new Wrapper<T>();
            wrapper.Items = array;
            return JsonUtility.ToJson(wrapper, prettyPrint);
        }

        [Serializable]
        private class Wrapper<T> {
            public T[] Items;
        }
    }
    public abstract class Actions {
        public string name;
        public string dist;
        public List<string> available = new List<string>();
        public float forward = 0.0f;
        public float moveRight = 0.0f;
        public float turnRight = 0.0f;

        public abstract void SetAction(List<float> stepAction);
    }
    public class DiscreteActions : Actions {

        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "discrete");
            Debug.Assert(stepAction.Count == 1, "in the discrete case step action must be of length 1");

            // in the case of discrete actions, this list is just one value
            // the value is casted to an int, this is a bit hacky and I am sure there is a more elegant way to do this.
            int iStepAction = (int)stepAction[0];
            // Clear previous actions
            forward = 0.0f;
            moveRight = 0.0f;
            turnRight = 0.0f;
            switch (available[iStepAction]) {
                case "move_forward":
                    forward = 1.0f;
                    break;
                case "move_backward":
                    forward = -1.0f;
                    break;
                case "move_left":
                    moveRight = 1.0f;
                    break;
                case "move_right":
                    moveRight = -1.0f;
                    break;
                case "turn_left":
                    turnRight = -1.0f;
                    break;
                case "turn_right":
                    turnRight = 1.0f;
                    break;
                default:
                    Debug.Assert(false, "invalid action");
                    break;
            }
        }
    }

    public class ContinuousActions : Actions {
        public override void SetAction(List<float> stepAction) {
            Debug.Assert(dist == "continuous");
            Debug.Assert(stepAction.Count == available.Count, "step action and avaiable count mismatch");

            for (int i = 0; i < stepAction.Count; i++) {
                switch (available[i]) {
                    case "move_forward_backward":
                        forward = stepAction[i];
                        break;
                    case "move_left_right":
                        moveRight = stepAction[i];
                        break;
                    case "turn_left_right":
                        turnRight = stepAction[i];
                        break;
                    default:
                        Debug.Assert(false, "invalid action");
                        break;
                }
            }
        }

        public void Print() {

            Debug.Log("Printing actions");
            Debug.Log("name: " + name);
            Debug.Log("dist: " + dist);
            Debug.Log("name: " + name);
            foreach (var avail in available) {
                Debug.Log("type: " + avail);
            }
        }
    }

    [RequireComponent(typeof(CharacterController))]
    public class Agent : SimAgentBase {
        public float move_speed = 1f;
        public float turn_speed = 1f;
        public float height = 1f;
        private const bool HUMAN = false;

        public Color color = Color.white;

        CharacterController controller;
        Camera agent_camera;

        void Awake() {
            controller = GetComponent<CharacterController>();
            agent_camera = GetComponentInChildren<Camera>();
            if (HUMAN) {
                agent_camera.targetTexture = new RenderTexture(32, 32, 24); // for debugging
            }
        }

        public Actions actions;
        // Start is called before the first frame update
        void Start() {

        }

        void Update() {
            if (HUMAN) {
                AgentUpdate();
                ObservationCoroutine(null);
            }
        }
        public void Initialize(SimEnv.GLTF.HF_RL_agents.HF_RL_Agent agentData) {
            Initialize();
            SetProperties(agentData);
        }
        public void SetProperties(SimEnv.GLTF.HF_RL_agents.HF_RL_Agent agentData) {

            Debug.Log("Setting Agent properties");

            color = agentData.color;
            height = agentData.height;
            move_speed = agentData.move_speed;
            turn_speed = agentData.turn_speed;

            switch (agentData.action_dist) {

                case "discrete":
                    actions = new DiscreteActions();
                    break;
                case "continuous":
                    actions = new ContinuousActions();
                    break;
                default:
                    Debug.Assert(false, "action distribution was not discrete or continuous");
                    break;
            }

            actions.name = agentData.action_name;
            actions.dist = agentData.action_dist;
            actions.available = agentData.available_actions;

            agent_camera.targetTexture = new RenderTexture(agentData.camera_width, agentData.camera_height, 24);

        }
        public void AgentUpdate() {

            if (HUMAN) {
                // Human control
                float x = Input.GetAxis("Horizontal");
                float z = Input.GetAxis("Vertical");
                float r = 0.0f;

                Vector3 move = transform.right * x + transform.forward * z;

                transform.Rotate(Vector3.up * r);
                if (Input.GetKeyUp("r")) {
                    Debug.Log("Agent reset");
                    transform.position = new Vector3(0.0f, 0.0f, 0.0f);
                }
            } else {
                // RL control
                Vector3 move = transform.right * actions.moveRight + transform.forward * actions.forward;
                controller.Move(move * move_speed * Time.deltaTime);
                float rotate = actions.turnRight;
                transform.Rotate(Vector3.up * rotate * turn_speed);
            }
        }

        public void ObservationCoroutine(UnityAction<string> callback) {
            StartCoroutine(RenderCoroutine(callback));
        }

        IEnumerator RenderCoroutine(UnityAction<string> callback) {
            yield return new WaitForEndOfFrame();
            GetObservation(callback);
            Debug.Log("Finished rendering");

        }

        public void GetObservation(UnityAction<string> callback) {

            RenderTexture activeRenderTexture = RenderTexture.active;
            RenderTexture.active = agent_camera.targetTexture;
            agent_camera.Render();
            int width = agent_camera.pixelWidth;
            int height = agent_camera.pixelHeight;

            Texture2D image = new Texture2D(width, height);
            image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            image.Apply();

            Color32[] pixels = image.GetPixels32();
            RenderTexture.active = activeRenderTexture;

            uint[] pixel_values = new uint[pixels.Length * 3];

            for (int i = 0; i < pixels.Length; i++) {
                pixel_values[i * 3] += pixels[i].r;
                pixel_values[i * 3 + 1] += pixels[i].g;
                pixel_values[i * 3 + 2] += pixels[i].b;
                // we do not include alpha, TODO: Add option to include Depth Buffer
            }

            string string_array = JsonHelper.ToJson(pixel_values);
            if (callback != null)
                callback(string_array);

        }

        public void SetAction(List<float> step_action) {
            actions.SetAction(step_action);
        }
    }


}