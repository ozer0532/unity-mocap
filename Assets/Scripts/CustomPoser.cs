using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CustomPoser : MonoBehaviour
{
    public PoseParser Parser;
    public CustomKeypoint JointKeypoint;
    public CustomKeypoint TargetKeypoint;
    public Transform Joint;
    public Vector3 RotationalOffset;
    public Vector3 TargetDirection;

    [Header("Threshold")]
    public float StartThreshold;
    public float EndThreshold;

    private bool _moving;
    private Vector3 _prevDir = Vector3.right;

    public void HandlePose(float[,] poseKeypoints) {
        var rotation = FindRotationByOffset(poseKeypoints);
        SetRotation(rotation);
    }

    public void SetRotation(Quaternion rotation) {
        Joint.localRotation = Quaternion.Euler(RotationalOffset) * rotation;
    }

    private Quaternion FindRotationByOffset(float[,] keypoints) {
        var currPos = JointKeypoint.GetKeypointValue(keypoints);
        var tarPos = TargetKeypoint.GetKeypointValue(keypoints);
        var deltaPos = tarPos - currPos;
        var targetDir = TargetDirection;
        
        var threshold = _moving ? EndThreshold : StartThreshold;
        if (Vector3.Angle(_prevDir, targetDir) < threshold) {
            targetDir = _prevDir;
            _moving = false;
        }
        else {
            _prevDir = targetDir;
            _moving = true;
        }

        Transform parentJoint = Joint.parent;
        if (parentJoint) {
            deltaPos = parentJoint.InverseTransformDirection(deltaPos);
        }

        var rotation = Quaternion.FromToRotation(TargetDirection, deltaPos);

        return rotation;
    }

    private void Start() {
        if (Parser) {
            Parser.OnDataReceived += HandlePose;
        }
    }
}
