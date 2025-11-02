using System.Text;
using UnityEngine;
using Newtonsoft.Json.Linq;

public class TugOfWarCommands : MonoBehaviour , IGameCommands
{
    public void ExecuteCommand(string uuid, string username, string command, JObject parameters)
    {
        StringBuilder builder = new StringBuilder();
        builder.AppendLine("From the Tug of war Handler");
        builder.AppendLine(uuid);
        builder.AppendLine(username);
        builder.AppendLine(command);
        builder.AppendLine(parameters.ToString());
        Debug.Log(builder.ToString());
        
        switch (command)
        {
            case "pull":
                // Check of that uuid is a real player
                // Send to Tug of War controller who is pulling for what team
            case "create":
                GameObject prefab = GameObject.CreatePrimitive(PrimitiveType.Cube);
                prefab.name = uuid;
                Instantiate(prefab, transform.position, Quaternion.identity);
                break;
            default:
                return;
        }
    }
}
