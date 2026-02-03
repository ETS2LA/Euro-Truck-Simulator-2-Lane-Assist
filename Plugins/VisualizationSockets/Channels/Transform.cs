using ETS2LA.Logging;
using ETS2LA.Shared;
using ETS2LA.Backend;
using System.Net.WebSockets;
using ETS2LA.Backend.Events;

namespace VisualizationSockets.Channels;

public class TransformChannel : IWebsocketChannel
{
    private Plugin? _plugin;
    private WebSocket? _socket;
    public string Name => "Transform";
    public string Description => "Sends the current transform (position, rotation) of the truck.";
    public int Channel => 1;
    public WebSocketChannelType ChannelType => WebSocketChannelType.Continuous;

    GameTelemetryData? _data;

    public void Init(Plugin plugin, WebSocket socket)
    {
        _plugin = plugin;
        _socket = socket;
        Events.Current.Subscribe<GameTelemetryData>("GameTelemetry.Data", OnTelemetryUpdate);   
    }

    public void OnTelemetryUpdate(GameTelemetryData data)
    {
        _data = data;
        SendData(_socket!);
    }

    public async void SendData(WebSocket socket)
    {
        if (_plugin == null) return;

        var output = new
        {
            channel = Channel,
            data = new
            {
                x = _data?.truckPlacement.coordinate.X ?? 0f,
                y = _data?.truckPlacement.coordinate.Y ?? 0f,
                z = _data?.truckPlacement.coordinate.Z ?? 0f,
                sector_x = 0,
                sector_y = 0,
                rx = _data?.truckPlacement.rotation.X ?? 0f,
                ry = _data?.truckPlacement.rotation.Y ?? 0f,
                rz = _data?.truckPlacement.rotation.Z ?? 0f,
            }
        };

        var json = System.Text.Json.JsonSerializer.Serialize(output);
        var buffer = System.Text.Encoding.UTF8.GetBytes(json);
        
        try
        {
            if (socket.State != WebSocketState.Open)
                return;
            await socket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
        } 
        catch (WebSocketException) 
        {
            Logger.Info($"Client [dim]{socket.GetHashCode()}[/] disconnected.");
        }
    }

    public void Shutdown()
    {
        Events.Current.Unsubscribe<GameTelemetryData>("GameTelemetry.Data", OnTelemetryUpdate);
    }
}