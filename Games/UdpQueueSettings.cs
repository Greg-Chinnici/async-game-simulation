using UnityEngine;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;


[CreateAssetMenu(fileName = "UdpQueueSettings", menuName = "Scriptable Objects/UdpQueueSettings")]
public class UdpQueueSettings : ScriptableObject
{
    [Header("Network Settings")]
    public int port = 9000;
    public bool allowRemoteConnections = false;
    public List<string> ips = new (){ 
        "::1",
        "127.0.0.1"
        };
    
    [HideInInspector]
    public HashSet<IPAddress> ipTable;
    
    public void Initialize()
        {
            ipTable = new HashSet<IPAddress>();
            foreach (var ip in ips)
            {
                if (IPAddress.TryParse(ip, out var parsed))
                    ipTable.Add(parsed);
            }
        }
}

