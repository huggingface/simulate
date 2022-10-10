using UnityEngine;
using Simulate;

public class DoorAI : MonoBehaviour {
    enum State {
        Closed,
        Open,
        Opening,
        Closing
    }

    State state;
    float t;

    void Awake() {
        state = State.Closed;
        t = 0;
    }

    public void Step() {
        switch (state) {
            case State.Opening:
                t = Mathf.Min(1, t + Config.instance.timeStep);
                if (t == 1) {
                    state = State.Open;
                    return;
                }
                break;
            case State.Closing:
                t = Mathf.Max(0, t - Config.instance.timeStep);
                if (t == 0) {
                    state = State.Closed;
                    return;
                }
                break;
        }
        transform.rotation = Quaternion.Euler(0, 90 * t, 0);
    }

    public void Open() {
        state = State.Opening;
    }
}