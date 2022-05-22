// https://vinnik-dmitry07.medium.com/a-python-unity-interface-with-zeromq-12720d6b7288
using NetMQ;
using System;
using System.Collections.Concurrent;
using System.ComponentModel;
using System.Linq;
using UnityEngine;

public class Client : MonoBehaviour
{
    public DataParserSO parser;

    private readonly ConcurrentQueue<Action> runOnMainThread = new ConcurrentQueue<Action>();
    private Receiver receiver;

    public void Start()
    {   
        AsyncIO.ForceDotNet.Force();

        receiver = new Receiver();
        receiver.Start((object data) => runOnMainThread.Enqueue(() =>
            {
                parser.HandleData(data);
            }
        ));
    }

    public void Update()
    {
        if (!runOnMainThread.IsEmpty)
        {
            Action action;
            while (runOnMainThread.TryDequeue(out action))
            {
                action.Invoke();
            }
        }
    }

    private void OnDestroy()
    {
        receiver.Stop();
        NetMQConfig.Cleanup();  // Must be here to work more than once
    }
}