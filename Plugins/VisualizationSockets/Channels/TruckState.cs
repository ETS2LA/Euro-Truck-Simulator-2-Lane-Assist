using ETS2LA.Logging;
using ETS2LA.Shared;
using ETS2LA.Backend;
using System.Net.WebSockets;
using ETS2LA.Backend.Events;

namespace VisualizationSockets.Channels;

public class TruckStateChannel : IWebsocketChannel
{
    private Plugin? _plugin;
    private WebSocket? _socket;
    public string Name => "Truck State";
    public string Description => "Sends the current state (throttle, steering, blinkers...) of the truck.";
    public int Channel => 3;
    public WebSocketChannelType ChannelType => WebSocketChannelType.Continuous;

    GameTelemetryData? _data;

    public void Init(Plugin plugin, WebSocket socket)
    {
        _plugin = plugin;
        _socket = socket;
        Events.Current.Subscribe<GameTelemetryData>("GameTelemetry.Data", OnTelemetryUpdate);   
        Task.Run(() => SenderThread());
    }

    public void OnTelemetryUpdate(GameTelemetryData data)
    {
        _data = data;
    }

    private void SenderThread()
    {
        while (_socket != null && _socket.State == WebSocketState.Open)
        {
            SendData(_socket);
            System.Threading.Thread.Sleep(50); // 20 FPS
        }
    }

    public async void SendData(WebSocket socket)
    {
        if (_plugin == null) return;

        var output = new
        {
            channel = Channel,
            data = new
            {
                speed = _data?.truckFloat.speed ?? 0f,
                speed_limit = _data?.truckFloat.speedLimit ?? 0f,
                cruise_control = 0f,
                target_speed = 0f,
                throttle = _data?.truckFloat.gameThrottle ?? 0f,
                brake = _data?.truckFloat.gameBrake ?? 0f,
                indicating_left = _data?.truckBool.blinkerLeftActive ?? false,
                indicating_right = _data?.truckBool.blinkerRightActive ?? false,
                indicator_left = _data?.truckBool.blinkerLeftOn ?? false,
                indicator_right = _data?.truckBool.blinkerRightOn ?? false,
                game = _data?.scsValues.game ?? "Unknown",
                time = _data?.commonUI.timeAbsolute
            }
        };

        var json = System.Text.Json.JsonSerializer.Serialize(output);
        var buffer = System.Text.Encoding.UTF8.GetBytes(json);
        
        try
        {
            if (socket.State != WebSocketState.Open)
                return;

            await WebsocketLock.Current.Semaphore.WaitAsync();
            await socket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
        } 
        catch (WebSocketException) 
        {
            Logger.Info($"Client [dim]{socket.GetHashCode()}[/] disconnected.");
        }
        finally
        {
            WebsocketLock.Current.Semaphore.Release();
        }
    }

    public void Shutdown()
    {
        Events.Current.Unsubscribe<GameTelemetryData>("GameTelemetry.Data", OnTelemetryUpdate);
    }
}