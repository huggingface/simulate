using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class Cart : MonoBehaviour {
    public float moveForce = 300f;
    public float rotationDampening = 200f;

    Rigidbody rigidBody;
    Vector3 prevPos;
    float push;

    void Awake() {
        rigidBody = GetComponent<Rigidbody>();
        prevPos = transform.position;
    }

    void Update() {
        push = 0;
        if (Input.GetKey(KeyCode.LeftArrow))
            push -= 1;
        if (Input.GetKey(KeyCode.RightArrow))
            push += 1;

        Ray ray = new Ray(transform.position, Vector3.down);
        float deltaPosition = (transform.position - prevPos).magnitude;
        if (Physics.Raycast(ray, out RaycastHit hit, 1f, LayerMask.GetMask("Ground"))) {
            transform.up = Vector3.Lerp(transform.up, hit.normal, Time.deltaTime * deltaPosition * rotationDampening);
        }

        prevPos = transform.position;
    }

    void FixedUpdate() {
        rigidBody.AddForce(Vector3.right * push * moveForce * Time.fixedDeltaTime, ForceMode.Acceleration);
    }
}