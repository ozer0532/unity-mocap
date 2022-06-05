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

    [Header("Threshold")]
    public float TiltStartThreshold;
    public float YawStartThreshold;
    public float TiltEndThreshold;
    public float YawEndThreshold;

    [SerializeField] private bool _debug;

    private float[,] _poseKeypoints;
    private Vector3 _prevUp = Vector3.up;
    private Vector3 _prevForward = Vector3.forward;
    private bool _tilting;
    private bool _yawing;

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

        if (Vector3.Angle(_prevUp, up) < (_tilting ? TiltEndThreshold : TiltStartThreshold)) {
            up = _prevUp;
            _tilting = false;
        }
        else {
            _prevUp = up;
            _tilting = true;
        }
        if (Vector3.Angle(_prevForward, forward) < (_yawing ? YawEndThreshold : YawStartThreshold)) {
            forward = _prevForward;
            _yawing = false;
        }
        else {
            _prevForward = forward;
            _yawing = true;
        }

        var rotation = Quaternion.identity;
        var tiltRot = Quaternion.FromToRotation(parentUp, up);
        var yawRot = Quaternion.FromToRotation(parentForward, forward);
        rotation *= tiltRot;
        rotation *= yawRot;

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
