using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HeadPoserV2 : MonoBehaviour
{
    public PoseParser Parser;
    public CustomKeypoint MouthKeypoint;
    public CustomKeypoint EyesKeypoint;
    public CustomKeypoint LeftKeypoint;
    public CustomKeypoint RightKeypoint;
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
    private Vector3 _prevLtr = Vector3.forward;
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
        // Joint.localRotation = rotation;
    }

    private Quaternion FindRotation(float[,] keypoints) {
        Transform parentJoint = Joint.parent;
        var parentUp = Vector3.up;
        var parentRight = Vector3.right;
        if (parentJoint) {
            parentUp = parentJoint.up;
            parentRight = parentJoint.right;
        }

        var mouth = MouthKeypoint.GetKeypointValue(keypoints);
        var eyes = EyesKeypoint.GetKeypointValue(keypoints);
        var left = LeftKeypoint.GetKeypointValue(keypoints);
        var right = RightKeypoint.GetKeypointValue(keypoints);

        var up = eyes - mouth;
        var ltr = right - left;

        if (Vector3.Angle(_prevUp, up) < (_tilting ? TiltEndThreshold : TiltStartThreshold)) {
            up = _prevUp;
            _tilting = false;
        }
        else {
            _prevUp = up;
            _tilting = true;
        }
        if (Vector3.Angle(_prevLtr, ltr) < (_yawing ? YawEndThreshold : YawStartThreshold)) {
            ltr = _prevLtr;
            _yawing = false;
        }
        else {
            _prevLtr = ltr;
            _yawing = true;
        }

        var rotation = Quaternion.identity;
        var tiltRot = Quaternion.FromToRotation(parentUp, up);
        // tiltRot *= Quaternion.Inverse(Quaternion.AngleAxis(tiltRot.eulerAngles.y, up));
        var yawRot = Quaternion.FromToRotation(parentRight, ltr);
        rotation *= tiltRot;
        rotation *= yawRot;

        print(parentRight);
        print(ltr);
        print(Vector3.Angle(parentRight, ltr));

        // rotation = Quaternion.LookRotation(Vector3.Cross(ltr, up), up);

        // if (parentJoint) {
        //     rotation *= Quaternion.Inverse(parentJoint.rotation);
        // }

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
            var eyes = EyesKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;
            var left = LeftKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;
            var right = RightKeypoint.GetKeypointValue(_poseKeypoints) + Vector3.up;

            Gizmos.DrawWireSphere(mouth, 0.01f);
            Gizmos.DrawWireSphere(eyes, 0.01f);
            Gizmos.DrawWireSphere(left, 0.01f);
            Gizmos.DrawWireSphere(right, 0.01f);
            Gizmos.DrawLine(mouth, eyes);
            Gizmos.DrawLine(left, right);

            Gizmos.color = temp;
        }
    }
}
