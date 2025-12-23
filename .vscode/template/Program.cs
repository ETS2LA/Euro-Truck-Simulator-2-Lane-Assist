using ETS2LA.Shared;

[assembly: PluginInformation("ETS2LAPlugin", "Describe your plugin here.")]
namespace ETS2LAPlugin
{
    public class ETS2LAPlugin : Plugin
    {
        public override void Init()
        {
            base.Init();
            // Initialization code here
            // e.g., subscribe to events
            // _bus?.Subscribe<YourEventType>("YourTopic", YourEventHandler);
        }

        public override void Tick()
        {
            // This will be run at the specified TickRate when the plugin is enabled.
            // You can use `public override float TickRate => 10f;` to change the tick rate to whatever FPS you want.
            // Please do not use a tick rate higher than what you need, that uses extra performance.

            // If your code works exclusively off of events you can remove this override. In this case unless your code
            // is purely a library, you should check if _IsRunning is true in your even handlers to avoid processing
            // events when the user has set the plugin to disabled.
        }
    }
}