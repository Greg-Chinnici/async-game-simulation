using UnityEngine;
using Newtonsoft.Json.Linq;
public interface IGameCommands 
{
    public void ExecuteCommand(string uuid , string username , string command , JObject parameters);
}
