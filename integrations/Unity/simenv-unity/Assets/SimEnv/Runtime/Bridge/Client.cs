using System;
using System.Net.Sockets;
using System.Text;
using System.Collections;
using UnityEngine;
using System.Linq;
using System.Collections.Generic;

namespace SimEnv {
    [CreateAssetMenu(menuName = "SimEnv/Client")]
    public class Client : Singleton<Client> {
        public string host;
        public int port;

        TcpClient _client;
        TcpClient client {
            get {
                _client ??= new TcpClient(host, port);
                return _client;
            }
        }

        Dictionary<string, ICommand> _commands;
        Dictionary<string, ICommand> commands {
            get {
                _commands ??= new Dictionary<string, ICommand>();
                return _commands;
            }
        }

        Coroutine listenCoroutine;

        /// <summary>
        /// Connect to server and begin listening for commands.
        /// </summary>
        public void Initialize(string host = "localhost", int port = 55000) {
            if(TryGetArg("port", out string portArg))
                int.TryParse(portArg, out port);
            this.host = host;
            this.port = port;
            LoadCommands();
            if (listenCoroutine == null)
                listenCoroutine = ListenCoroutine().RunCoroutine();
        }

        /// <summary>
        /// Helper function for getting command line arguments.
        /// </summary>
        /// <param name="name"></param>
        /// <returns></returns>
        public static bool TryGetArg(string name, out string arg) {
            arg = null;
            var args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++) {
                if (args[i] == name && args.Length > i + 1) {
                    arg = args[i + 1];
                    return true;
                }
            }
            return false;
        }

        private void LoadCommands() {
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && x.GetInterfaces().Contains(typeof(ICommand)))
                .Select(x => (ICommand)Activator.CreateInstance(x))
                .ToList().ForEach(command => {
                    string type = command.GetType().Name;
                    if (!commands.ContainsKey(type))
                        commands.Add(type, command);
                });
        }

        private IEnumerator ListenCoroutine() {
            int chunkSize = 1024;
            byte[] buffer = new byte[chunkSize];
            while (true) {
                NetworkStream stream = client.GetStream();
                if (stream.DataAvailable) {
                    byte[] lengthBuffer = new byte[4];
                    stream.Read(lengthBuffer, 0, 4);

                    int messageLength = BitConverter.ToInt32(lengthBuffer, 0);
                    byte[] data = new byte[messageLength];
                    int dataReceived = 0;

                    while (dataReceived < messageLength)
                        dataReceived += stream.Read(data, dataReceived, Math.Min(chunkSize, messageLength - dataReceived));

                    Debug.Assert(dataReceived == messageLength);
                    string message = Encoding.ASCII.GetString(data, 0, messageLength);
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

        /// <summary>
        /// Write a message back to the server.
        /// </summary>
        /// <param name="message"></param>
        public void WriteMessage(string message) {
            if (client == null) return;
            try {
                NetworkStream stream = client.GetStream();
                if (stream.CanWrite) {
                    byte[] buffer = Encoding.ASCII.GetBytes(message);
                    byte[] lengthBytes = BitConverter.GetBytes(buffer.Length);
                    Debug.Assert(lengthBytes.Length == 4);
                    stream.Write(lengthBytes, 0, 4);
                    stream.Write(buffer, 0, buffer.Length);
                    //Debug.Log("Sent message: " + message);
                }
            } catch (Exception e) {
                Debug.Log("Socket error: " + e);
            }
        }

        /// <summary>
        /// Close the client.
        /// </summary>
        public void Close() {
            if (client != null && client.Connected)
                client.Close();
        }

        private bool TryParseCommand(string json, out ICommand command, out string error) {
            error = "";
            command = null;
            CommandWrapper commandWrapper = JsonUtility.FromJson<CommandWrapper>(json);
            if (!commands.ContainsKey(commandWrapper.type)) {
                error = "Unknown command: " + commandWrapper.type;
                return false;
            }
            command = commands[commandWrapper.type];
            JsonUtility.FromJsonOverwrite(commandWrapper.contents, command);
            return true;
        }

        [Serializable]
        private class CommandWrapper {
            public string type;
            public string contents;
        }
    }
}