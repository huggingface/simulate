using UnityEngine;

public class Cart : MonoBehaviour {
    public float rotationDampening = 10f;

    void Update() {
        Ray ray = new Ray(transform.position, Vector3.down);
        if (Physics.Raycast(ray, out RaycastHit hit, 1f, LayerMask.GetMask("Ground"))) {
            transform.up = Vector3.Lerp(transform.up, hit.normal, Time.deltaTime * rotationDampening);
        }
    }
}