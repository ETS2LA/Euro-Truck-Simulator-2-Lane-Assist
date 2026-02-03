using ETS2LA.Logging;
using ETS2LA.Shared;
using System.Net;
using System.Net.WebSockets;

namespace VisualizationSockets
{
    public class VisualizationSockets : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "VisualizationSockets",
            Description = "This plugin provides socket-based data for visualizations outside of ETS2LA.",
            AuthorName = "Tumppi066",
        };

        HttpListener? _listener;

        public override void Init()
        {
            base.Init();
        }

        public override void OnEnable()
        {
            base.OnEnable();
            _listener = new HttpListener();
            _listener.Prefixes.Add("http://localhost:37522/");
            _listener.Start();
            Logger.Info("Visualization WebSocket started on ws://localhost:37522/");
        }

        public async override void Tick()
        {
            if (_listener == null || !_listener.IsListening)
                return;

            var context = await _listener.GetContextAsync();
            if (context.Request.IsWebSocketRequest)
            {
                HttpListenerWebSocketContext wsContext = await context.AcceptWebSocketAsync(null);
                WebSocket socket = wsContext.WebSocket;
                Logger.Info($"Opened new WebSocket connection from {wsContext.Origin} ([dim]{socket.GetHashCode()}[/])");
                await Task.Run(() => WebSocketHandler(socket));
            }
            else
            {
                context.Response.StatusCode = 400;
                context.Response.Close();
            }
        }

        private IWebsocketChannel? ChannelToObject(int channel)
        {
            return channel switch
            {
                1 => new Channels.TransformChannel(),
                _ => null
            };
        }

        private async void WebSocketHandler(WebSocket socket)
        {
            List<IWebsocketChannel> channels = new List<IWebsocketChannel>();

            byte[] buffer = new byte[1024];
            while (socket.State == WebSocketState.Open)
            {
                WebSocketReceiveResult result;
                try 
                { 
                    result = await socket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None); 
                } 
                catch (WebSocketException) 
                {
                    Logger.Info($"Client [dim]{socket.GetHashCode()}[/] disconnected.");
                    foreach (var ch in channels)
                    {
                        ch.Shutdown();
                    }
                    channels.Clear();
                    await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                    break;
                }

                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                }
                else
                {
                    // Decode the input message
                    string message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                    var input = System.Text.Json.JsonSerializer.Deserialize<ClientWebsocketMessage>(message);
                    if (input == null) continue;

                    var channel = input.channel;
                    var method = input.method;

                    if (method == "subscribe")
                    {
                        var channelObj = ChannelToObject(channel);
                        if (channelObj != null)
                        {
                            channelObj.Init(this, socket);
                            channels.Add(channelObj);
                            Logger.Info($"Client subscribed to channel {channel} ({channelObj.Name})");
                        }
                        continue;
                    }
                    else if (method == "unsubscribe")
                    {
                        channels.RemoveAll(c => c.Channel == channel);
                        Logger.Info($"Client unsubscribed from channel {channel}");
                        continue;
                    }

                    if (method == "acknowledge")
                    {
                        foreach (var ch in channels)
                        {
                            if (ch.ChannelType == WebSocketChannelType.Responsive)
                            {
                                ch.SendData(socket);
                            }
                        }
                    }
                }
            }
        }
        
        public override void OnDisable()
        {
            base.OnDisable();
            _listener?.Stop();
            _listener?.Close();
        }

        public override void Shutdown()
        {
            base.Shutdown();
            _listener?.Stop();
            _listener?.Close();
            // This is run once when the plugin is unloaded (at app shutdown), use it to clean up any resources or
            // threads you created in Init or elsewhere.
        }
    }
}