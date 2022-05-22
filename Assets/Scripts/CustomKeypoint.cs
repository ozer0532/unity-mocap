using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class CustomKeypoint : ScriptableObject
{
    public abstract Vector3 GetKeypointValue(float[,] keypoints);
}
