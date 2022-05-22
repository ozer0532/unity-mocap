using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "Custom Keypoint", menuName = "Mocap/Keypoint/Basic")]
public class Keypoint : CustomKeypoint
{
    public int index;
    public override Vector3 GetKeypointValue(float[,] keypoints)
    {
        return new Vector3(keypoints[index, 0], keypoints[index, 1], keypoints[index, 2]);
    }
}
