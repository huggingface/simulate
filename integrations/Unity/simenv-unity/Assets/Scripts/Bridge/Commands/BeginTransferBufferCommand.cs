using UnityEngine.Events;

public class BeginTransferBuffer : Command
{
    public string name;
    public int length;

    public override void Execute(UnityAction<string> callback) {
        Client.ListenForBuffer(name, length);
        callback("ack");
    }
}
