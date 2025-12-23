using ETS2LA.Logging;
using Spectre.Console;
using Velopack;

namespace ETS2LA.Backend
{
    public class Program
    {
        public EventBus? bus;
        public PluginHandler? pluginHandler;

        public void Main(string[] args)
        {
            // Run Velopack for update checking
            VelopackApp.Build().Run();

            bus = new EventBus();
            pluginHandler = new PluginHandler(bus);

            Logger.Console.Status().Start("Starting ETS2LA...", ctx =>
            {
                pluginHandler.LoadPlugins();

                //pluginHandler.EnablePlugin(pluginName: "ExampleProvider.MyProvider");
                pluginHandler.EnablePlugin(pluginName: "ExampleConsumer.MyConsumer");

                // RenCloud's Game Telemetry plugin provider
                pluginHandler.EnablePlugin(pluginName: "GameTelemetry.GameTelemetry");
                // ets2la_plugin providers and consumers
                pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.CameraProvider");
                pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.TrafficProvider");
                pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.SemaphoreProvider");
                pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.NavigationProvider");
                pluginHandler.EnablePlugin(pluginName: "ETS2LASDK.OutputConsumer");
                // scs-sdk-controller consumer
                pluginHandler.EnablePlugin(pluginName: "ControlsSDK.EventConsumer");

                Thread.Sleep(1000);
                Logger.Success("ETS2LA is running.");
            });
        }

        public void Shutdown()
        {
            if (pluginHandler != null)
            {
                pluginHandler.UnloadPlugins();
            }
            Logger.Info("ETS2LA has been shut down.");
        }
    }
}