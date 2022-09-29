using System;
using System.Net.Sockets;
using System.Text;
using System.Collections;
using UnityEngine;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Simulate {
    [CreateAssetMenu(menuName = "Simulate/Client")]
    public class Client : Singleton<Client> {
        public static string host;
        public static int port;
        private static bool isOpen = false;

        static TcpClient _client;
        static TcpClient client {
            get {
                _client ??= new TcpClient(host, port);
                return _client;
            }
        }

        static Dictionary<string, ICommand> _commands;
        static Dictionary<string, ICommand> commands {
            get {
                _commands ??= new Dictionary<string, ICommand>();
                return _commands;
            }
        }

        static Coroutine listenCoroutine;

        /// <summary>
        /// Connect to server and begin listening for commands.
        /// </summary>
        public static void Initialize(string host = "localhost", int port = 55001) {
            Client.host = host;
            Client.port = port;
            LoadCommands();
            isOpen = true;
            if(listenCoroutine == null)
                listenCoroutine = ListenCoroutine().RunCoroutine();
        }

        private static void LoadCommands() {
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(x => x.GetTypes())
                .Where(x => !x.IsInterface && !x.IsAbstract && x.GetInterfaces().Contains(typeof(ICommand)))
                .Select(x => (ICommand)Activator.CreateInstance(x))
                .ToList().ForEach(command => {
                    string type = command.GetType().Name;
                    if(!commands.ContainsKey(type))
                        commands.Add(type, command);
                    else
                        Debug.LogWarning("Found multiple commands of type " + type);
                });
        }

        private static IEnumerator ListenCoroutine() {
            int chunkSize = 1024;
            byte[] buffer = new byte[chunkSize];
            while(isOpen) {
                NetworkStream stream = client.GetStream();
                if(stream.DataAvailable) {
                    byte[] lengthBuffer = new byte[4];
                    stream.Read(lengthBuffer, 0, 4);

                    int messageLength = BitConverter.ToInt32(lengthBuffer, 0);
                    byte[] data = new byte[messageLength];
                    int dataReceived = 0;

                    while(dataReceived < messageLength)
                        dataReceived += stream.Read(data, dataReceived, Math.Min(chunkSize, messageLength - dataReceived));

                    Debug.Assert(dataReceived == messageLength);
                    string json = Encoding.ASCII.GetString(data, 0, messageLength);
                    TryExecuteCommand(json);
                }
                yield return null;
            }
        }

        /// <summary>
        /// Write a message back to the server.
        /// </summary>
        /// <param name="message"></param>
        public static void WriteMessage(string message) {
            if(client == null || !isOpen) return;
            try {
                NetworkStream stream = client.GetStream();
                if(stream.CanWrite) {
                    byte[] buffer = Encoding.ASCII.GetBytes(message);
                    byte[] lengthBytes = BitConverter.GetBytes(buffer.Length);
                    Debug.Assert(lengthBytes.Length == 4);
                    stream.Write(lengthBytes, 0, 4);
                    stream.Write(buffer, 0, buffer.Length);
                }
            } catch(Exception e) {
                Debug.Log("Socket error: " + e);
            }
        }

        /// <summary>
        /// Close the client.
        /// </summary>
        public static void Close() {
            isOpen = false;
            if(client != null && client.Connected)
                client.Close();
        }

        private static void TryExecuteCommand(string json) {
            JObject jObject = JObject.Parse(json);
            Dictionary<string, JToken> tokens = jObject.Properties()
                .ToDictionary(x => x.Name, x => x.Value);
            if(!tokens.TryGetValue("type", out JToken type)) {
                string error = "Command doesn't contain type";
                Debug.LogWarning(error);
                WriteMessage(error);
                return;
            }
            Dictionary<string, object> kwargs = new Dictionary<string, object>();
            foreach(string key in tokens.Keys) {
                if(key == "type")
                    continue;
                object value = tokens[key].ToObject<object>();
                kwargs.Add(key, value);
            }

            // Try to find the command by name
            if(!commands.TryGetValue(type.ToString(), out ICommand command)) {
                string error = "Unknown command: " + type;
                Debug.LogWarning(error);
                WriteMessage(error);
                return;
            }

            // Populate class with kwargs
            JsonConvert.PopulateObject(JsonConvert.SerializeObject(kwargs), command);

            // Try to execute the command
            try {
                command.Execute(kwargs, result => WriteMessage(result));
            } catch(System.Exception e) {
                Debug.LogWarning(e.ToString());
                WriteMessage(e.ToString());
            }
        }
    }
}