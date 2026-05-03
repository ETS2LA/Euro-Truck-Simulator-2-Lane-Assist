using Huskui.Avalonia.Controls;
using Huskui.Avalonia.Models;
using System.Numerics;

namespace ETS2LA.Shared
{
    /// <summary>
    ///  The EventBus is used by plugins to communicate with each other.
    /// </summary>
    /// <remarks>
    ///  Plugins can subscribe to topics and publish data to topics. When data is published to a topic,
    ///  all subscribers to that topic will receive the data.
    /// </remarks>
    public interface IEventBus
    {
        /// <summary>
        ///  Subscribe to an event topic with a handler. Please call this function in `OnEnable` and do not call it in `Init`. <br/>
        ///  Remember to call `Unsubscribe` in `OnDisable` and `Shutdown` as well!
        /// </summary>
        /// <typeparam name="T">The type of the expected response.</typeparam>
        /// <param name="topic">The topic string, usually PluginName.SomeTopic</param>
        /// <param name="handler">The handler to call when this event fires.</param>
        void Subscribe<T>(string topic, Action<T> handler);
        /// <summary>
        ///  Unsubscribe from an event topic.
        /// </summary>
        /// <typeparam name="T">The type of the expected response.</typeparam>
        /// <param name="topic">The topic string, usually PluginName.SomeTopic</param>
        /// <param name="handler">The handler to unsubscribe from this topic.</param>
        void Unsubscribe<T>(string topic, Action<T> handler);
        /// <summary>
        ///  Publish an event to a topic. All subscribers to this topic will receive the data.
        /// </summary>
        /// <typeparam name="T">The type of the data being published.</typeparam>
        /// <param name="topic">The topic string, usually PluginName.SomeTopic</param>
        /// <param name="data">The data to publish.</param>
        void Publish<T>(string topic, T data);
    }

    /// <summary>
    ///  The base interface for all ETS2LA plugins.
    /// </summary>
    public interface IPlugin
    {
        /// <summary>
        ///  This plugin's information such as it's name, description, author, etc.
        /// </summary>
        PluginInformation Info { get; }
        /// <summary>
        ///  Whether this plugin is currently running. Set by the backend, do not edit.
        /// </summary>
        bool _IsRunning { get; set; }
        /// <summary>
        ///  This function is ran once when the plugin is loaded, use it to setup any static data. <br/>
        ///  **NOTE**: Do not access the EventBus here, use `OnEnable` for that!
        /// </summary>
        void Init();
        /// <summary>
        ///  This function is ran when the plugin is enabled. Use it to subscribe to events. <br/>
        ///  Remember to unsubscribe in `OnDisable` and `Shutdown` as well!
        /// </summary>
        void OnEnable();
        /// <summary>
        ///  The main tick function. Equivalent to `Update()` in Unity and `Tick()` in Unreal Engine. <br/>
        ///  This function is ran at the rate defined by `TickRate`, as long as the CPU allows.
        /// </summary>
        void Tick();
        /// <summary>
        ///  This function is ran when the plugin is disabled. Use it to unsubscribe from events
        ///  and stop any running tasks. 
        /// </summary>
        void OnDisable();
        /// <summary>
        ///  This function is ran when the plugin is unloaded, usually at app shutdown. 
        ///  Use it to cleanup any resources.
        /// </summary>
        void Shutdown();
    }

    /// <summary>
    ///  The base class for all ETS2LA plugins.
    /// </summary>
    public abstract class Plugin : IPlugin
    {
        public abstract PluginInformation Info { get; }
        public bool _IsRunning { get; set; } = false;
        /// <summary>
        ///  The tick rate of this plugin in ticks per second. Default is 20.0f TPS. <br/>
        ///  Please do not use a tickrate higher than you need, that will just wait CPU time.
        /// </summary>
        public virtual float TickRate => 20.0f;

        public virtual void Init() { }

        public virtual void OnEnable()
        {
            _IsRunning = true;
            Task.Run(() => RunningThread());
        }

        /// <summary>
        ///  The main running thread of this plugin. Handles ticking at the defined TickRate.
        /// </summary>
        protected void RunningThread()
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            double interval = 1000.0 / TickRate; // ms per tick
            double next = sw.Elapsed.TotalMilliseconds;

            while (_IsRunning)
            {
                // Update interval in case TickRate changed
                interval = 1000.0 / TickRate;

                next += interval;
                try { Tick(); } 
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in plugin {Info.Name} Tick: {ex}");
                }
                double remaining = next - sw.Elapsed.TotalMilliseconds;

                // Use Thread.Sleep for the bigger part of the sleep.
                // This is not accurate, but saves CPU.
                if (remaining > 1.0)
                    System.Threading.Thread.Sleep((int)(remaining - 1));

                // Busy-wait the last bit for better accuracy. This uses some CPU,
                // but ensures we get a stable tickrate.
                while (_IsRunning && sw.Elapsed.TotalMilliseconds < next)
                    System.Threading.Thread.SpinWait(10);
            }
        }

        public virtual void Tick() { }

        public virtual void OnDisable()
        {
            _IsRunning = false;
        }
        public virtual void Shutdown()
        {
            _IsRunning = false;
        }
    }

    /// <summary>
    ///  Represents the basic information about a plugin.
    /// </summary>
    public class PluginInformation
    {
        // Required
        public required string Name { get; set; }
        public required string Description { get; set; }

        // Optional
        /// <summary>
        ///  Use commas to separate multiple authors.
        /// </summary>
        public string AuthorName { get; set; } = "";
        /// <summary>
        ///  Use commas to separate multiple author websites.
        /// </summary>
        public string AuthorWebsite { get; set; } = "";
        /// <summary>
        ///  Use commas to separate multiple author icons.
        /// </summary>
        public string AuthorIcon { get; set; } = "";
        public string[] Tags { get; set; } = Array.Empty<string>();
    }

    // Utility Classes
    public class Vector3Double
    {
        public double X;
        public double Y;
        public double Z;

        public Vector3Double(double x, double y, double z)
        {
            X = x;
            Y = y;
            Z = z;
        }

        public override string ToString()
        {
            return $"({X}, {Y}, {Z})";
        }

        public static Vector3Double Zero => new Vector3Double(0, 0, 0);
        public static Vector3Double One => new Vector3Double(1, 1, 1);

        public double[] ToArray()
        {
            return new double[] { X, Y, Z };
        }

        public Vector3 ToVector3()
        {
            return new Vector3((float)X, (float)Y, (float)Z);
        }

        public static Vector3Double operator -(Vector3Double a, Vector3Double b)
        {
            return new Vector3Double(a.X - b.X, a.Y - b.Y, a.Z - b.Z);
        }

        public static Vector3Double operator +(Vector3Double a, Vector3Double b)
        {
            return new Vector3Double(a.X + b.X, a.Y + b.Y, a.Z + b.Z);
        }

        public static Vector3Double operator *(Vector3Double a, double b)
        {
            return new Vector3Double(a.X * b, a.Y * b, a.Z * b);
        }

        public static Vector3Double operator /(Vector3Double a, double b)
        {
            return new Vector3Double(a.X / b, a.Y / b, a.Z / b);
        }
    }
}