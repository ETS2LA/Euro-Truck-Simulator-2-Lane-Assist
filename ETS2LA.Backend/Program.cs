using ETS2LA.Logging;
using Velopack;

namespace ETS2LA.Backend
{
    public static class Program
    {
        static EventBus? _bus;
        static PluginHandler? _pluginHandler;

        static void Main(string[] args)
        {
            // Run Velopack for update checking
            VelopackApp.Build().Run();

            _bus = new EventBus();
            _pluginHandler = new PluginHandler(_bus);

            Logger.Info("Starting ETS2LA...");
            _pluginHandler.LoadPlugins();
            
            //_pluginHandler.EnablePlugin(pluginName: "ExampleProvider.MyProvider");
            _pluginHandler.EnablePlugin(pluginName: "ExampleConsumer.MyConsumer");
            
            // RenCloud's Game Telemetry plugin provider
            _pluginHandler.EnablePlugin(pluginName: "GameTelemetry.GameTelemetry");
            // ets2la_plugin providers
            _pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.CameraProvider");
            _pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.TrafficProvider");
            _pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.SemaphoreProvider");
            _pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.NavigationProvider");

            // Sleep the main thread until the application is closed
            Logger.Info("ETS2LA is running. Press Enter to exit.");
            Console.ReadLine();
        }
    }
}