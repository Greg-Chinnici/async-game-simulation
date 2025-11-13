using System;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Newtonsoft.Json.Linq;

public class UDPCommandListenerWithQueue : MonoBehaviour
{
    public UdpQueueSettings settings;
    public MonoBehaviour gameCommandHandler; 
    private IGameCommands commandHandler;

    private UdpClient udpClient;
    private Thread listenerThread;

    // Thread-safe queue for commands
    private readonly ConcurrentQueue<CommandData> commandQueue = new ConcurrentQueue<CommandData>();

    void Start()
    {
        commandHandler = gameCommandHandler as IGameCommands;
        if (commandHandler == null)
        {
            Debug.LogError("[UDP] gameCommandHandler must implement IGameCommands");
            return;
        }
        settings.Initialize();
        
        IPAddress bindAddress = settings.allowRemoteConnections ? IPAddress.Any : IPAddress.Loopback;

        udpClient = new UdpClient(new IPEndPoint(bindAddress, settings.port));

        listenerThread = new Thread(ListenLoop);
        listenerThread.IsBackground = true;
        listenerThread.Start();

        Debug.Log("[UDP] Listening on port " + settings.port);
        
        
        DontDestroyOnLoad(gameObject);
    }

    void OnApplicationQuit()
    {
        udpClient?.Close();
        listenerThread?.Abort();
    }

    private void ListenLoop()
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any ,  0);

        while (true)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEP);
                if (!settings.ipTable.Contains(remoteEP.Address))
                {
                    Debug.LogWarning($"[UDP] Blocked packet from {remoteEP.Address}");
                    continue;
                }
                
                string json = Encoding.UTF8.GetString(data);
                try
                {
                    JObject commandObj = JObject.Parse(json);
                    
                    string uuid = commandObj.Value<string>("uuid");
                    
                    string username = commandObj.Value<string>("username");
                    string command = commandObj.Value<string>("command");
                    JObject parameters = commandObj.Value<JObject>("params");
                    long seq = commandObj.Value<long?>("seq") ?? 0;

                    // Enqueue for main-thread execution
                    commandQueue.Enqueue(new CommandData(uuid, username, command, parameters));
                }
                catch (Exception ex)
                {
                    Debug.LogError("[UDP] JSON parse or command error: " + ex);
                }
            }
            catch (SocketException se)
            {
                Debug.LogError("[UDP] SocketException: " + se);
            }
            catch (Exception ex)
            {
                Debug.LogError("[UDP] Listener exception: " + ex);
            }
        }
    }

    void FixedUpdate()
    {
        // Process all queued commands safely on the main thread
        while (commandQueue.TryDequeue(out CommandData cmd))
        {
            commandHandler.ExecuteCommand(cmd.UUID, cmd.Username, cmd.Command, cmd.Parameters);
        }
    }

    private struct CommandData
    {
        public string UUID;
        public string Username;
        public string Command;
        public JObject Parameters;

        public CommandData(string uuid, string username, string command, JObject parameters)
        {
            UUID = uuid;
            Username = username;
            Command = command;
            Parameters = parameters;
        }
    }
}

