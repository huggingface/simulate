using SimEnv;
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class Cart : MonoBehaviour {
    public float moveForce = 300f;
    public float rotationDampening = 10f;

    Rigidbody rigidBody;
    float push;

    void Awake() {
        rigidBody = GetComponent<Rigidbody>();
    }

    void Update() {
        push = 0;
        if (Input.GetKey(KeyCode.LeftArrow))
            push -= 1;
        if (Input.GetKey(KeyCode.RightArrow))
            push += 1;

        UpdateRotation();
    }

    void UpdateRotation() {
        Ray ray = new Ray(transform.position, Vector3.down);
        if (Physics.Raycast(ray, out RaycastHit hit, 1f, LayerMask.GetMask("Ground"))) {
            transform.up = Vector3.Lerp(transform.up, hit.normal, Time.deltaTime * rotationDampening);
        }
    }

    void FixedUpdate() {
        rigidBody.AddForce(Vector3.right * push * moveForce * Time.fixedDeltaTime, ForceMode.Acceleration);
    }
}