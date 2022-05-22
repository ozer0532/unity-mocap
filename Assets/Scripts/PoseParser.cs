using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

[CreateAssetMenu(fileName = "Pose Parser", menuName = "Mocap/Pose Parser")]
public class PoseParser : DataParserSO
{
    // Events & Delegates
    public event Action<float[,]> OnDataReceived;

    public override void HandleData(object data)
    {
        if (data is not null) {
            var parseResult = Parse(data);

            OnDataReceived?.Invoke(parseResult);
        }
    }

    public float[,] Parse(object data)
    {
        var arr = (object[]) data;

        float[,] mulArr = new float[arr.Length, ((object[])arr[0]).Length];
        for (int i = 0; i < mulArr.GetLength(0); i++) {
            object[] row = (object[])arr[i];
            for (int j = 0; j < mulArr.GetLength(1); j++) {
                mulArr[i, j] = (float)row[j];
            }
        }

        return mulArr;
    }

    private void OnDisable() {
        OnDataReceived = null;
    }
}
