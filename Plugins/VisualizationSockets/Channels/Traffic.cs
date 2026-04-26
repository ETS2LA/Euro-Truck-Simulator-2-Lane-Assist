using ETS2LA.Logging;
using ETS2LA.Shared;
using ETS2LA.Game.SDK;
using ETS2LA.Backend.Events;

using System.Net.WebSockets;
using System.Text.Json.Serialization;
using System.Text.Json;
using TruckLib;

namespace VisualizationSockets.Channels;

public class TrafficChannel : IWebsocketChannel
{
    private Plugin? _plugin;
    private WebSocket? _socket;
    public string Name => "Traffic";
    public string Description => "Sends traffic data, includes all traffic vehicles and objects (TODO!).";
    public int Channel => 4;
    public WebSocketChannelType ChannelType => WebSocketChannelType.Continuous;
    public JsonSerializerOptions JsonOptions => new JsonSerializerOptions
    {
        NumberHandling = JsonNumberHandling.AllowNamedFloatingPointLiterals
    };

    TrafficData? _data;

    public void Init(Plugin plugin, WebSocket socket)
    {
        _plugin = plugin;
        _socket = socket;
        Events.Current.Subscribe<TrafficData>("ETS2LASDK.Traffic", OnTrafficUpdate);
        Task.Run(() => SenderThread());
    }

    public void OnTrafficUpdate(TrafficData data)
    {
        _data = data;
    }

    private void SenderThread()
    {
        while (_socket != null && _socket.State == WebSocketState.Open)
        {
            int start = Environment.TickCount;
            SendData(_socket);
            int end = Environment.TickCount;
            int elapsed = end - start;
            System.Threading.Thread.Sleep(Math.Max(50 - elapsed, 0)); // 20 FPS
        }
    }

    public async void SendData(WebSocket socket)
    {
        if (_plugin == null) return;
        if (_data == null) return;

        var output = new
        {
            channel = Channel,
            data = new
            {
                vehicles = _data?.vehicles.Select(v => new
                {
                    position = new
                    {
                        x = v.position.X,
                        y = v.position.Y,
                        z = v.position.Z,
                    },
                    rotation = new
                    {
                        x = v.rotation.X,
                        y = v.rotation.Y,
                        z = v.rotation.Z,
                        w = v.rotation.W,
                        yaw = v.rotation.ToEulerDeg().Y,
                        pitch = v.rotation.ToEulerDeg().X,
                        roll = v.rotation.ToEulerDeg().Z,
                    },
                    size = new
                    {
                        width = v.size.X,
                        height = v.size.Y,
                        length = v.size.Z,
                    },
                    speed = v.speed,
                    acceleration = v.acceleration,
                    trailer_count = v.trailer_count,
                    id = v.id,
                    trailers = v.trailers.Select(t => new
                    {
                        position = new
                        {
                            x = t.position.X,
                            y = t.position.Y,
                            z = t.position.Z,
                        },
                        rotation = new
                        {
                            x = t.rotation.X,
                            y = t.rotation.Y,
                            z = t.rotation.Z,
                            w = t.rotation.W,
                            yaw = t.rotation.ToEulerDeg().Y,
                            pitch = t.rotation.ToEulerDeg().X,
                            roll = t.rotation.ToEulerDeg().Z,
                        },
                        size = new
                        {
                            width = t.size.X,
                            height = t.size.Y,
                            length = t.size.Z,
                        },
                    }).ToArray(),
                    is_tmp = v.isTMP,
                    is_trailer = v.isTrailer,
                })
            }
        };

        var json = JsonSerializer.Serialize(output, options: JsonOptions);
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
        _socket = null;
        Events.Current.Unsubscribe<TrafficData>("ETS2LASDK.Traffic", OnTrafficUpdate);
    }
}