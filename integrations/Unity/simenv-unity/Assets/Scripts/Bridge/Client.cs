using System;
using System.Net.Sockets;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;
using System.Text;

public class Client : MonoBehaviour
{
    public static Client Instance { get; private set; }

    static string pendingBufferName;
    static int pendingBufferLength;

    [SerializeField] string host = "localhost";
    [SerializeField] int port = 55000;

    Queue<string> messageQueue = new Queue<string>();
    Thread clientThread;
    TcpClient client;
    object asyncLock = new object();

    void Awake() {
        Instance = this;
        pendingBufferName = null;
        pendingBufferLength = 0;
    }

    void OnEnable() {
        try {
            clientThread = new Thread(new ThreadStart(Listen));
            clientThread.IsBackground = true;
            clientThread.Start();
        } catch(Exception e) {
            Debug.Log("Client exception: " + e);
        }
    }

    void OnDisable() {
        if(client != null && client.Connected)
            client.Close();
    }

    void Update() {
        lock(asyncLock) {
            while(messageQueue.Count > 0) {
                string json = messageQueue.Dequeue();
                Command command = Command.Parse(json);
                Debug.Log("Executing command: " + command.GetType().ToString());
                command.Execute(OnFinishedRunningCommand);
            }
        }
    }

    void Listen() {
        try {
            client = new TcpClient(host, port);
            byte[] buffer = new byte[65535];
            while(true) {
                using (NetworkStream stream = client.GetStream()) {
                    int length;
                    while((length = stream.Read(buffer, 0, buffer.Length)) != 0) {
                        if(string.IsNullOrEmpty(pendingBufferName)) {
                            string message = Encoding.ASCII.GetString(buffer, 0, length);
                            Debug.Log("Received message: " + message);
                            lock(asyncLock)
                                messageQueue.Enqueue(message);
                        } else {
                            Debug.Log(string.Format("Received buffer {0}", pendingBufferName));
                            byte[] bytes = new byte[pendingBufferLength];
                            Array.Copy(buffer, bytes, pendingBufferLength);
                            SimEnv.WriteBuffer(pendingBufferName, bytes);
                            pendingBufferName = null;
                            OnFinishedRunningCommand("ack");
                        }
                    }
                }
            }
        } catch(Exception e) {
            Debug.Log("Disconnected: " + e);
        }
    }

    void OnFinishedRunningCommand(string response) {
        if(client == null) return;
        try {
            NetworkStream stream = client.GetStream();
            if(stream.CanWrite) {
                byte[] buffer = Encoding.ASCII.GetBytes(response);
                stream.Write(buffer, 0, buffer.Length);
                Debug.Log("Sent message: " + response);
            }
        } catch(Exception e) {
            Debug.Log("Socket error: " + e);
        }
    }

    public static void ListenForBuffer(string bufferName, int length) {
        Debug.Assert(string.IsNullOrEmpty(pendingBufferName), "Already waiting for buffer " + pendingBufferName);
        pendingBufferName = bufferName;
        pendingBufferLength = length;
        Debug.Log("Listening for buffer: " + pendingBufferName);
    }
}
