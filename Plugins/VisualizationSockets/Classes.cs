using System.Net;
using System.Net.WebSockets;
using ETS2LA.Shared;

namespace VisualizationSockets;

public enum WebSocketChannelType
{
    Responsive,
    Continuous
}

public interface IWebsocketChannel
{
    string Name { get; }
    string Description { get; }
    int Channel { get; }
    WebSocketChannelType ChannelType { get; }
    void Init(Plugin plugin, WebSocket socket);
    void SendData(WebSocket socket);
    void Shutdown();
}

[Serializable]
public class ClientWebsocketMessage
{
    public int channel { get; set; }
    public string method { get; set; }

    public ClientWebsocketMessage(int channel, string method)
    {
        this.channel = channel;
        this.method = method;
    }
}

public class WebsocketLock
{
    private static readonly Lazy<WebsocketLock> _instance = new(() => new WebsocketLock());
    public static WebsocketLock Current => _instance.Value;
    public SemaphoreSlim Semaphore = new SemaphoreSlim(1, 1);
}