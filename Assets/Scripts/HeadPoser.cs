using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeadPoser : MonoBehaviour
{
    public PoseParser Parser;
    public CustomKeypoint MouthKeypoint;
    public CustomKeypoint NoseKeypoint;
    public CustomKeypoint EyesKeypoint;
    public Transform Joint;
    public Vector3 RotationalOffset;

    [SerializeField] private bool _debug;

    private float[,] _poseKeypoints;

    public void HandlePose(float[,] poseKeypoints) {
        var rotation = FindRotation(poseKeypoints);
        SetRotation(rotation);

        if (_debug) {
            _poseKeypoints = poseKeypoints;
        }
    }

    public void SetRotation(Quaternion rotation) {
        Joint.localRotation = Quaternion.Euler(RotationalOffset) * rotation;
    }

    private Quaternion FindRotation(float[,] keypoints) {
        Transform parentJoint = Joint.parent;
        var parentUp = Vector3.up;
        var parentForward = Vector3.forward;
        if (parentJoint) {
            parentUp = parentJoint.up;
            parentForward = parentJoint.forward;
        }

        var mouth = MouthKeypoint.GetKeypointValue(keypoints);
        var nose = NoseKeypoint.GetKeypointValue(keypoints);
        var eyes = EyesKeypoint.GetKeypointValue(keypoints);

        var up = eyes - mouth;
        var forward = nose - (mouth + (up * 0.5f));

        var rotation = Quaternion.FromToRotation(parentUp, up);
        rotation = rotation * Quaternion.FromToRotation(parentForward, forward);

        // print(Vector3.Angle(parentUp, up));

        if (parentJoint) {
            rotation *= Quaternion.Inverse(parentJoint.rotation);
        }

        return rotation;
    }

    private void Start() {
        if (Parser) {
            Parser.OnDataReceived += HandlePose;
        }
    }
    
    private void OnDrawGizmos() {
        if (_debug && _poseKeypoints != null) {
            Color temp = Gizmos.color;
            Gizmos.color = Color.green;

            var mouth = MouthKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;
            var nose = NoseKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;
            var eyes = EyesKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;

            Gizmos.DrawWireSphere(mouth, 0.01f);
            Gizmos.DrawWireSphere(eyes, 0.01f);
            Gizmos.DrawWireSphere(nose, 0.01f);
            Gizmos.DrawLine(mouth, eyes);

            Gizmos.color = temp;
        }
    }
}
