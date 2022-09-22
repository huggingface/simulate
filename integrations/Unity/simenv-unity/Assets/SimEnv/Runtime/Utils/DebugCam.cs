using UnityEngine;

namespace Simulate {
    [RequireComponent(typeof(Camera))]
    public class DebugCam : MonoBehaviour {
        public float acceleration = 50; // how fast you accelerate
        public float accSprintMultiplier = 4; // how much faster you go when "sprinting"
        public float lookSensitivity = 1; // mouse look sensitivity
        public float dampingCoefficient = 5; // how quickly you break to a halt after you stop your input
        public bool focusOnEnable = true; // whether or not to focus and lock cursor immediately on enable

        Vector3 velocity; // current velocity

        private Vector3 centre = new Vector3(0f, 0f, 0f);

        static bool Focused {
            get => Cursor.lockState == CursorLockMode.Locked;
            set {
                Cursor.lockState = value ? CursorLockMode.Locked : CursorLockMode.None;
                Cursor.visible = value == false;
            }
        }

        void OnEnable() {
            if (focusOnEnable) Focused = true;
        }

        void OnDisable() => Focused = false;

        void Start() {
            transform.position = new Vector3(7.24f, 19f, -4f);
            transform.LookAt(centre, Vector3.up);
        }
        void Update() {
            // Input
            if (Focused)
                UpdateInput();
            else if (Input.GetMouseButtonDown(0))
                Focused = true;

            // Physics
            velocity = Vector3.Lerp(velocity, Vector3.zero, dampingCoefficient * Time.deltaTime);
            transform.position += velocity * Time.deltaTime;

            //transform.RotateAround(centre, Vector3.up, 10.0f * Time.deltaTime);
            // Leave cursor lock
            if (Input.GetKeyDown(KeyCode.Escape))
                Focused = false;

        }

        void UpdateInput() {
            // Position
            velocity += GetAccelerationVector() * Time.deltaTime;

            // Rotation
            Vector2 mouseDelta = lookSensitivity * new Vector2(Input.GetAxis("Mouse X"), -Input.GetAxis("Mouse Y"));
            Quaternion rotation = transform.rotation;
            Quaternion horiz = Quaternion.AngleAxis(mouseDelta.x, Vector3.up);
            Quaternion vert = Quaternion.AngleAxis(mouseDelta.y, Vector3.right);
            transform.rotation = horiz * rotation * vert;

            // Leave cursor lock
            if (Input.GetKeyDown(KeyCode.Escape))
                Focused = false;
        }

        Vector3 GetAccelerationVector() {
            Vector3 moveInput = default;

            void AddMovement(KeyCode key, Vector3 dir) {
                if (Input.GetKey(key))
                    moveInput += dir;
            }

            AddMovement(KeyCode.W, Vector3.forward);
            AddMovement(KeyCode.S, Vector3.back);
            AddMovement(KeyCode.D, Vector3.right);
            AddMovement(KeyCode.A, Vector3.left);
            AddMovement(KeyCode.Space, Vector3.up);
            AddMovement(KeyCode.LeftControl, Vector3.down);
            Vector3 direction = transform.TransformVector(moveInput.normalized);

            if (Input.GetKey(KeyCode.LeftShift))
                return direction * (acceleration * accSprintMultiplier); // "sprinting"
            return direction * acceleration; // "walking"
        }
    }
}