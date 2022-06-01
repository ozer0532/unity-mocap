using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SpinnyCamera : MonoBehaviour
{
    public float Sensitivity = 1;

    Vector2 _prevPos = Vector2.zero;

    private void LateUpdate() {
        Vector2 input = Input.mousePosition;
        Vector2 delta = input - _prevPos;
        _prevPos = input;

        Vector3 axis = Vector3.Cross(delta, Vector3.forward);
        float angle = delta.magnitude * Sensitivity;

        if (Input.GetMouseButton(0)) {
            var q = Quaternion.AngleAxis(angle, axis);
            transform.rotation *= q;
            transform.localEulerAngles = new Vector3(
                transform.localEulerAngles.x,
                transform.localEulerAngles.y,
                0
            );
        }
    }
}
