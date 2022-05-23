using System;
using System.Net.Sockets;
using System.Text;
using System.Collections;
using UnityEngine;
using ISimEnv;
using System.Linq;

namespace SimEnv {
    /// <summary>
    /// Manages all communication with Python API
    /// </summary>
    public class Client {
        TcpClient client;
        string host;
        int port;

        public Client(string host = "localhost", int port = 55000) {
            this.host = host;
            this.port = port;
        }

        public IEnumerator Listen() {
            try {
                client = new TcpClient(host, port);
            } catch (Exception e) {
                Debug.LogError("Connection failed: " + e.ToString());
                yield break;
            }
            int chunk_size = 1024;
            byte[] buffer = new byte[chunk_size];
            while (true) {
                NetworkStream stream = client.GetStream();
                if (stream.DataAvailable) {
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
                    if (TryParseCommand(message, out ICommand command, out string error)) {
                        command.Execute(response => WriteMessage(response));
                    } else {
                        Debug.LogWarning(error);
                        WriteMessage(error);
                    }
                }
                yield return null;
            }
        }

        public void WriteMessage(string message) {
            if (client == null) return;
            try {
                NetworkStream stream = client.GetStream();
                if (stream.CanWrite) {
                    byte[] buffer = Encoding.ASCII.GetBytes(message);
                    stream.Write(buffer, 0, buffer.Length);
                    Debug.Log("Sent message: " + message);
                }
            } catch (Exception e) {
                Debug.Log("Socket error: " + e);
            }
        }

        public void Close() {
            if (client != null && client.Connected)
                client.Close();
        }

        bool TryParseCommand(string json, out ICommand command, out string error) {
            error = "";
            command = null;
            CommandWrapper commandWrapper = JsonUtility.FromJson<CommandWrapper>(json);
            Type commandType = AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => x.IsSubclassOf(typeof(ICommand)))
                .FirstOrDefault(x => x.ToString().EndsWith(commandWrapper.type));
            if (commandType == null) {
                error = "Unknown Command " + commandWrapper.type;
                return false;
            }
            command = JsonUtility.FromJson(commandWrapper.contents, commandType) as ICommand;
            return true;
        }

        [Serializable]
        private class CommandWrapper {
            public string type;
            public string contents;
        }
    }
}