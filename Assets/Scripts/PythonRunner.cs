using System.Diagnostics;
using System.IO;
using System.Text;

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PythonRunner : MonoBehaviour
{
    public RunMode Mode;

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
        var fileName = Directory.GetCurrentDirectory() + @"\venv\Scripts\python.exe";

        var psi = new ProcessStartInfo();
        // point to python virtual env
        psi.FileName = Directory.GetCurrentDirectory();
        psi.FileName += @"\venv\Scripts\python.exe";

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
        strCmdText= string.Format("{0} ", script);
        System.Diagnostics.Process.Start(fileName, strCmdText);
    }

    public enum RunMode {
        Triangulation,
        Inference,
        Averaging,
    }
}
