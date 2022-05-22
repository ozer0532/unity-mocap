using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "Custom Keypoint", menuName = "Mocap/Keypoint/Average")]
public class AverageKeypoint : CustomKeypoint
{
    public int[] KeypointIndices;

    public override Vector3 GetKeypointValue(float[,] keypoints)
    {
        int count = 0;
        var sum = new Vector3();

        foreach (var keypoint in KeypointIndices)
        {
            count++;
            sum[0] += keypoints[keypoint, 0];
            sum[1] += keypoints[keypoint, 1];
            sum[2] += keypoints[keypoint, 2];
        }

        sum[0] /= count;
        sum[1] /= count;
        sum[2] /= count;

        return sum;
    }
}
