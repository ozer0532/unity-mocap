using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HipPoser : MonoBehaviour
{
    public PoseParser Parser;
    public CustomKeypoint LeftHip;
    public CustomKeypoint RightHip;
    public Transform Joint;
    public Vector3 RotationalOffset;

    public void HandlePose(float[,] poseKeypoints) {
        var rotation = FindRotationByOffset(poseKeypoints);
        SetRotation(rotation);
    }

    public void SetRotation(Quaternion rotation) {
        Joint.localRotation = Quaternion.Euler(RotationalOffset) * rotation;
    }

    private Quaternion FindRotationByOffset(float[,] keypoints) {
        var left = LeftHip.GetKeypointValue(keypoints);
        var right = RightHip.GetKeypointValue(keypoints);
        var ltr = right - left;

        var angle = Vector3.SignedAngle(Vector3.right, ltr, Vector3.up);
        var rotation = Quaternion.AngleAxis(angle, Vector3.up);

        return rotation;
    }

    private void Start() {
        if (Parser) {
            Parser.OnDataReceived += HandlePose;
        }
    }
}
