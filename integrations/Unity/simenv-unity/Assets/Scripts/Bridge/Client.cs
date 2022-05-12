using System;
using System.Net.Sockets;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;
using System.Text;

public class Client : MonoBehaviour {
    public static Client Instance { get; private set; }

    [SerializeField] string host = "localhost";
    [SerializeField] int port = 55000;

    Queue<string> messageQueue = new Queue<string>();
    Thread clientThread;
    TcpClient client;
    object asyncLock = new object();

    void Awake() {
        Instance = this;
    }

    void OnEnable() {
        try {
            clientThread = new Thread(new ThreadStart(Listen));
            clientThread.IsBackground = true;
            clientThread.Start();
        } catch (Exception e) {
            Debug.Log("Client exception: " + e);
        }
    }

    void OnDisable() {
        if (client != null && client.Connected)
            client.Close();
    }

    void Update() {
        lock (asyncLock) {
            while (messageQueue.Count > 0) {
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
            int chunk_size = 1024;
            byte[] buffer = new byte[chunk_size];
            while (true) {
                NetworkStream stream = client.GetStream();
                if(!stream.DataAvailable) continue;
                
                byte[] lengthBuffer = new byte[4];
                stream.Read(lengthBuffer, 0, 4);

                int messageLength = BitConverter.ToInt32(lengthBuffer, 0);
                byte[] data = new byte[messageLength];
                int dataReceived = 0;

                while (dataReceived < messageLength) {
                    dataReceived += stream.Read(data, dataReceived, Math.Min(chunk_size, messageLength - dataReceived));
                }

                Debug.Assert(dataReceived == messageLength);
                string message = Encoding.ASCII.GetString(data, 0, messageLength);
                Debug.Log("Received message: " + message);
                lock (asyncLock)
                    messageQueue.Enqueue(message);
            }
        } catch (Exception e) {
            Debug.Log("Disconnected: " + e);
        }
    }

    void OnFinishedRunningCommand(string response) {
        if (client == null) return;
        try {
            NetworkStream stream = client.GetStream();
            if (stream.CanWrite) {
                byte[] buffer = Encoding.ASCII.GetBytes(response);
                stream.Write(buffer, 0, buffer.Length);
                Debug.Log("Sent message: " + response);
            }
        } catch (Exception e) {
            Debug.Log("Socket error: " + e);
        }
    }
}
