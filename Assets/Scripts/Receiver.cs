// https://vinnik-dmitry07.medium.com/a-python-unity-interface-with-zeromq-12720d6b7288
using NetMQ;
using NetMQ.Sockets;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using UnityEngine;

public class Receiver
{
    private readonly Thread _receiveThread;
    private NetMQPoller _poller;

    public Receiver()
    {
        _receiveThread = new Thread((object callback) => 
        {
            using (var socket = new RequestSocket())
            {
                socket.Connect("tcp://localhost:5555");

                socket.SendFrameEmpty();

                using (_poller = new NetMQPoller {socket}) {
                    socket.ReceiveReady += (s, a) => {
                        byte[] message = a.Socket.ReceiveFrameBytes();

                        (var data, _) = Unpack(message);
                        ((Action<object>)callback)(data);
                        
                        // Poll ready
                        a.Socket.SendFrameEmpty();
                    };

                    _poller.Run();
                }
            }
        });
    }

    public void Start(Action<object> callback)
    {
        _receiveThread.Start(callback);
    }

    public void Stop()
    {
        _poller.Stop();
        _receiveThread.Join();
    }

    private byte[] ToBigEndian(byte[] data) {
        if (BitConverter.IsLittleEndian)
            Array.Reverse(data);
        return data;
    }

    private (object, byte[]) UnpackList(byte[] data) {
        var size = BitConverter.ToInt32(ToBigEndian(data[0..4]));
        var ret = new object[size];
        data = data[4..^0];

        for (var i = 0; i < size; i++) {
            (ret[i], data) = Unpack(data);
        }
        return (ret, data);
    } 

    private (object, byte[]) Unpack(byte[] data) {
        byte identifier = data[0];
        data = data[1..^0];

        if (identifier == 0x00) {
            return (null, data);
        } else if (identifier == 0x01) {
            return (BitConverter.ToInt32(ToBigEndian(data[0..4])), data[4..^0]);
        } else if (identifier == 0x02) {
            return (BitConverter.ToSingle(ToBigEndian(data[0..4])), data[4..^0]);
        } else if (identifier == 0x03) {
            return UnpackList(data);
        } else {
            throw new NotImplementedException($"Failed to unpack identifier with ID: {identifier}");
        }
    }
}