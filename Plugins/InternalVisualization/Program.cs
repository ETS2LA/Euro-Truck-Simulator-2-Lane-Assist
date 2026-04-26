using ETS2LA.Telemetry;
using ETS2LA.Overlay;
using ETS2LA.Shared;
using ETS2LA.Backend.Events;
using ETS2LA.Logging;

using ETS2LA.Game;
using ETS2LA.Game.Data;
using ETS2LA.Game.SiiFiles;
using ETS2LA.Game.PpdFiles;
using TruckLib.ScsMap;

using InternalVisualization.Renderers;

using Hexa.NET.ImGui;

namespace InternalVisualization
{
    public class InternalVisualization : Plugin
    {
        public override PluginInformation Info => new PluginInformation
        {
            Name = "InternalVisualization",
            Description = "Consectetur mollit ipsum velit Lorem fugiat aliqua officia exercitation exercitation.",
            AuthorName = "Developer",
        };

        private WindowDefinition _windowDefinition = new WindowDefinition
        {
            Title = "Internal Visualization",
            Width = 800,
            Height = 800,
        };

        public override float TickRate => 1f;
        private int ViewDistance = 300;

        private Renderer[] renderers = new Renderer[]
        {
            new NodesRenderer(),
            new RoadsRenderer(),
            new PrefabsRenderer(),
            new TrafficRenderer(),
            new TruckRenderer(),
            new StatisticsRenderer(),
        };

        private GameTelemetryData? _telemetryData;
        private MapData? _mapData;
        private Road[]? _roads;
        private Prefab[]? _prefabs;
        private IReadOnlyList<Node>? _nearbyNodes;

        public override void Init()
        {
            base.Init();
            // This is run once when the plugin is initially loaded.
            // Usually you start to listen to control events here (or register your own).
            // ControlsBackend.Current.On(ControlsBackend.Defaults.Next.Id, OnNextPressed);
        }

        public override void OnEnable()
        {
            base.OnEnable();
            OverlayHandler.Current.RegisterWindow(_windowDefinition, RenderWindow);

            // Subscribe to events here, do not subscribe in Init as that's too early.
            // Events.Current.Subscribe<YourEventType>("YourTopic", YourEventHandler);
            Events.Current.Subscribe<GameTelemetryData>(GameTelemetry.Current.EventString, OnTelemetryUpdated);
        }

        private void OnTelemetryUpdated(GameTelemetryData data)
        {
            _telemetryData = data;
        }

        public override void Tick()
        {
            int installation = 0;
            bool found = false;
            foreach (var item in GameHandler.Current.Installations)
            {
                if(item.IsParsed) {
                    found = true; 
                    break;
                }
                installation++;
            }

            if (!found) return;
            _mapData = GameHandler.Current.Installations[installation].GetMapData();
            var fs = GameHandler.Current.Installations[installation].GetFileSystem();
            if(fs != null) SiiFileHandler.Current.SetFileSystem(fs);
            if(fs != null) PpdFileHandler.Current.SetFileSystem(fs);

            _roads = _mapData.MapItems.Where(item => item is Road).Cast<Road>().ToArray();
            _prefabs = _mapData.MapItems.Where(item => item is Prefab).Cast<Prefab>().ToArray();

            if (_telemetryData == null) return;
            Vector3Double center = _telemetryData.truckPlacement.coordinate;
            double minX = center.X - ViewDistance;
            double maxX = center.X + ViewDistance;
            double minZ = center.Z - ViewDistance;
            double maxZ = center.Z + ViewDistance;
            _nearbyNodes = _mapData.Nodes.Within(minX, minZ, maxX, maxZ);
        }

        private void RenderWindow()
        {
            if(_telemetryData == null)
            {
                ImGui.Text("Waiting for telemetry data...");
                return;
            }
            if(_mapData == null || _roads == null || _prefabs == null || _nearbyNodes == null)
            {
                ImGui.Text("Waiting for map data...");
                return;
            }

            var drawList = ImGui.GetWindowDrawList();
            var windowSize = ImGui.GetWindowSize();
            var windowPos = ImGui.GetWindowPos();

            foreach (var renderer in renderers)
            {
                try
                {
                    renderer.Render(drawList, windowPos, windowSize, _telemetryData!, _mapData!, _roads!, _prefabs!, _nearbyNodes!);
                } catch(Exception e)
                {
                    Logger.Error($"Error rendering {renderer.GetType().Name}: {e}");
                    ImGui.Text($"Error rendering {renderer.GetType().Name}: {e}");
                }
            }
        }
        
        public override void OnDisable()
        {
            base.OnDisable();
            _mapData = null;
            OverlayHandler.Current.UnregisterWindow(_windowDefinition);
            // Unsubscribe from events here
            // Events.Current.Unsubscribe<YourEventType>("YourTopic", YourEventHandler);
        }

        public override void Shutdown()
        {
            base.Shutdown();
            // This is run once when the plugin is unloaded (at app shutdown), use it to clean up any resources or
            // threads you created in Init or elsewhere.
        }
    }
}