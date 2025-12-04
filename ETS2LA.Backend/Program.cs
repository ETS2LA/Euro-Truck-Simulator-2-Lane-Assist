using System;
using ETS2LA.Shared;

namespace ETS2LA.Backend
{
    public static class Program
    {
        static EventBus _bus = new EventBus();
        static PluginHandler _pluginHandler = new PluginHandler(_bus);

        static void Main(string[] args)
        {
            Console.WriteLine("Starting ETS2LA...");
            _pluginHandler.LoadPlugins();
            _pluginHandler.EnablePlugin(pluginName: "ExampleProvider.MyProvider");
            _pluginHandler.EnablePlugin(pluginName: "ExampleConsumer.MyConsumer");

            // Sleep the main thread until the application is closed
            Console.WriteLine("ETS2LA is running. Press Enter to exit.");
            Console.ReadLine();
        }
    }
}