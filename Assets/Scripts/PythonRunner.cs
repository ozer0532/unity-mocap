using System.Diagnostics;
using System.IO;
using System.Text;

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PythonRunner : MonoBehaviour
{
    [Header("Execution Settings")]
    public RunMode Mode;
    public int FirstCameraIndex;
    public int SecondCameraIndex;

    [Header("Python Location")]
    public string PythonPath = @"\venv\Scripts\python.exe";
    public bool AbsolutePath = false;

    // Start is called before the first frame update
    void Start()
    {
        RunPython();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void RunPython() 
    {
        string fileName;
        if (!AbsolutePath) fileName = Directory.GetCurrentDirectory() + PythonPath;
        else fileName = PythonPath;

        // Provide arguments
        string script;
        switch (Mode)
        {
            case RunMode.Triangulation:
                script = @"Assets\Python\cli_0tri.py";
                break;
            case RunMode.Inference:
                script = @"Assets\Python\cli_1inf.py";
                break;
            case RunMode.Averaging:
                script = @"Assets\Python\cli_2avg.py";
                break;
            default:
                throw new System.ArgumentException($"Unrecognized run mode {Mode}");
        }

        string strCmdText;
        strCmdText= string.Format("{0} -a {1} -b {2}", script, FirstCameraIndex, SecondCameraIndex);
        print($"Running {fileName} {strCmdText}");
        System.Diagnostics.Process.Start(fileName, strCmdText);
    }

    public enum RunMode {
        Triangulation,
        Inference,
        Averaging,
    }
}
