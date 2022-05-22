using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Poser : MonoBehaviour
{
    public MapInfo[] MappingInfo;
    public PoseParser Parser;

    [SerializeField] private bool _debug;

    private float _previousPollTime;
    private float _pollDeltaTime;
    private float[,] _poseKeypoints;
    private List<float> _pollDeltaTimes = new List<float>();

    private static readonly int[] _boneKeypointPairs = {
        11, 13, 13, 15, 15, 17, 17, 19, 19, 15, 15, 21,
        12, 14, 14, 16, 16, 18, 18, 20, 20, 16, 16, 22,
        11, 12, 12, 24, 24, 23, 23, 11,
        23, 25, 25, 27, 27, 29, 29, 31, 31, 27,
        24, 26, 26, 28, 28, 30, 30, 32, 32, 28,
    };

    public void HandlePose(float[,] poseKeypoints) {
        for (var i = 0; i < poseKeypoints.GetLength(0); i++)
        {
            // Debug.Log($"Handle keypoint {i}");

            var rotation = FindRotationByOffset(poseKeypoints, i);
            SetRotation(i, rotation);
        }

        if (_debug) {
            _pollDeltaTime = Time.unscaledTime - _previousPollTime;
            _previousPollTime = Time.unscaledTime;
            _poseKeypoints = poseKeypoints;
            _pollDeltaTimes.Add(_pollDeltaTime);
        }
    }

    public void SetRotation(int jointIndex, Quaternion rotation) {
        MapInfo mapInfo = MappingInfo[jointIndex];
        Transform joint = mapInfo.Joint;

        if (!joint) return;

        joint.localRotation = Quaternion.Euler(mapInfo.RotationalOffset) * rotation;
    }

    private Quaternion FindRotationByOffset(float[,] keypoints, int index) {
        var currMapInfo = MappingInfo[index];
        var tarIdx = currMapInfo.TargetIndex;

        if (tarIdx < 0) return Quaternion.identity;

        var targetMapInfo = MappingInfo[tarIdx];
        var currPos = new Vector3(keypoints[index, 0], keypoints[index, 1], keypoints[index, 2]);
        var tarPos = new Vector3(keypoints[tarIdx, 0], keypoints[tarIdx, 1], keypoints[tarIdx, 2]);
        var deltaPos = tarPos - currPos;
        var targetDir = currMapInfo.TargetDirection;

        Transform parentJoint = currMapInfo.Joint.parent;
        if (parentJoint) {
            deltaPos = parentJoint.InverseTransformDirection(deltaPos);
        }

        var rotation = Quaternion.FromToRotation(currMapInfo.TargetDirection, deltaPos);

        return rotation;
    }

    private void Start() {
        if (Parser) {
            Parser.OnDataReceived += HandlePose;
        }
    }

    private void OnDisable() {
        if (_debug) {
            print($"[{string.Join(", ", _pollDeltaTimes.ToArray())}]");
        }
    }

    private void OnDrawGizmos() {
        if (_debug && _poseKeypoints != null) {
            Color temp = Gizmos.color;
            Gizmos.color = Color.yellow;

            for (var i = 0; i < _poseKeypoints.GetLength(0); i++) {
                var position = new Vector3(
                    _poseKeypoints[i, 0],
                    _poseKeypoints[i, 1] + 1,
                    _poseKeypoints[i, 2]
                );
                Gizmos.DrawWireSphere(position, 0.01f);
            }

            Gizmos.color = Color.white;

            for (var i = 0; i < _boneKeypointPairs.Length; i += 2) {
                var from = _boneKeypointPairs[i];
                var to = _boneKeypointPairs[i + 1];
                var fromPt = new Vector3(
                    _poseKeypoints[from, 0],
                    _poseKeypoints[from, 1] + 1,
                    _poseKeypoints[from, 2]
                );
                var toPt = new Vector3(
                    _poseKeypoints[to, 0],
                    _poseKeypoints[to, 1] + 1,
                    _poseKeypoints[to, 2]
                );
                Gizmos.DrawLine(fromPt, toPt);
            }

            Gizmos.color = temp;
        }
    }

    private void OnGUI() {
        if (_debug) {
            GUI.Label(new Rect(10, 10, 200, 20), $"Frame per Second: {1/_pollDeltaTime:F4}");
        }
    }

    [System.Serializable]
    public class MapInfo {
        public string Name;
        public int TargetIndex = -1;
        public Transform Joint;
        public Vector3 RotationalOffset;
        public Vector3 TargetDirection;
    }
}
