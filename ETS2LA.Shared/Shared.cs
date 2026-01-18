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
    ///  Represents a notification sent in the bottom right corner of the ETS2LA UI.
    ///  Uses Huskui's GrowlItem system.
    /// </summary>
    public class Notification
    {
        /// <summary>
        ///  A unique identifier for this notification. For example: ExampleConsumer.SteeringOutput.
        /// </summary>
        public required string Id;
        /// <summary>
        ///  Indicates this notification was made by the notification system. Do not use.
        /// </summary>
        public bool IsInternal = false;
        /// <summary>
        ///  The time this notification was created, can be edited, but set to the current time by default.
        /// </summary>
        public DateTime CreatedAt = DateTime.UtcNow;
        /// <summary>
        ///  The GrowlItem this notification represents. Set by the notification system, don't use.
        /// </summary>
        public GrowlItem? Item = null;

        /// <summary>
        ///  The level of the notification, affects the color shown. <br/>
        ///  using Huskui.Avalonia.Models;     <br/>
        ///  GrowlLevel.Information; // Blue   <br/>
        ///  GrowlLevel.Success;     // Green  <br/>
        ///  GrowlLevel.Warning;     // Yellow <br/>
        ///  GrowlLevel.Danger;      // Red    <br/>
        /// </summary>
        public GrowlLevel Level = GrowlLevel.Information;
        /// <summary>
        ///  The title of the notification.
        /// </summary>
        public string Title = "";
        /// <summary>
        ///  The content of the notification.
        /// </summary>
        public string Content = "";

        /// <summary>
        ///  The progress of the notification progress bar. From 0.0f to 100.0f. <br/>
        ///  **NOTE**: Remember to set the `CloseAfter` parameter if you want to manually edit the progress bar! 
        /// </summary>
        public float Progress = 0.0f;
        /// <summary>
        ///  Whether the progress is indeterminate (i.e. a loading bar with no specified state).
        /// </summary>
        public bool IsProgressIndeterminate = false;

        /// <summary>
        ///  The time in seconds after which the notification will automatically close. <br/>
        ///  **NOTE**: Set to 0.0f if you want to manually edit the progress bar!
        /// </summary>
        public float CloseAfter = 8.0f; // seconds
        /// <summary>
        ///  The time in seconds after which the close button will be shown if CloseAfter is not set.
        /// </summary>
        public float ShowCloseButtonAfter = 0.0f; // seconds
    }

    public interface INotificationHandler
    {
        /// <summary>
        ///  Send a notification to be shown in the ETS2LA UI. This will update any existing notification with the same Id.
        /// </summary>
        /// <param name="notification"></param>
        void SendNotification(Notification notification);

        /// <summary>
        ///  Update an existing notification in the ETS2LA UI. In most situations it is recommended to use SendNotification instead.
        /// </summary>
        /// <param name="notification"></param>
        void UpdateNotification(Notification notification);

        /// <summary>
        ///  Close a notification in the ETS2LA UI.
        /// </summary>
        /// <param name="id"></param>
        void CloseNotification(string id);
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
        ///  This function is ran by the backend to register the plugin to the EventBus. <br/>
        ///  Please do not call this function yourself.
        /// </summary>
        /// <param name="bus"></param>
        void Register(IEventBus bus);
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
        /// <summary>
        ///  The EventBus this plugin is registered to. Set by the backend, do not edit.
        /// </summary>
        protected IEventBus? _bus;
        public bool _IsRunning { get; set; } = false;
        /// <summary>
        ///  The tick rate of this plugin in ticks per second. Default is 20.0f TPS. <br/>
        ///  Please do not use a tickrate higher than you need, that will just wait CPU time.
        /// </summary>
        public virtual float TickRate => 20.0f;

        public virtual void Init() { }
        public virtual void Register(IEventBus bus)
        {
            _bus = bus;
        }

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
                Tick();
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
            _bus = null;
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
    }

    /// <summary>
    ///  ETS2 -based quaternion class. Input values from the game to get a usable
    ///  quaternion representation. Implements conversion to Euler angles via `ToEuler()`.
    /// </summary>
    public class Quaternion
    {
        public float X;
        public float Y;
        public float Z;
        public float W;

        public Quaternion(float x, float y, float z, float w)
        {
            X = x;
            Y = y;
            Z = z;
            W = w;
        }

        public override string ToString()
        {
            return $"({X}, {Y}, {Z}, {W})";
        }

        public static Quaternion Identity => new Quaternion(0, 0, 0, 1);

        public float[] ToArray()
        {
            return new float[] { X, Y, Z, W };
        }

        public Vector3 ToEuler()
        {
            float yaw = (float)Math.Atan2(2.0 * (Y * Z + W * X), W * W - X * X - Y * Y + Z * Z);
            float pitch = (float)Math.Asin(-2.0 * (X * Z - W * Y));
            float roll = (float)Math.Atan2(2.0 * (X * Y + W * Z), W * W + X * X - Y * Y - Z * Z);

            yaw = yaw * (180.0f / (float)Math.PI);
            pitch = pitch * (180.0f / (float)Math.PI);
            roll = roll * (180.0f / (float)Math.PI);

            return new Vector3(pitch, roll, yaw);
        }
    }

    /// <summary>
    ///  This frame's camera data from the game. <br/>
    ///  **NOTE**: This might not match the telemetry in terms of timing!
    /// </summary>
    public class Camera
    {
        public float fov;
        /// <summary>
        ///  The position of the camera in the current sector. <br/> To convert to world
        ///  coordinates, add the sector's `cx` and `cy` offsets multiplied by 512.
        /// </summary>
        public Vector3 position = Vector3.Zero;
        public Int16 cx;
        public Int16 cy;
        public Quaternion rotation = Quaternion.Identity;
    }

    public class TrafficTrailer
    {
        public Vector3 position = Vector3.Zero;
        public Quaternion rotation = Quaternion.Identity;
        public Vector3 size = Vector3.Zero;
    }

    public class TrafficVehicle
    {
        public Vector3 position = Vector3.Zero;
        public Quaternion rotation = Quaternion.Identity;
        public Vector3 size = Vector3.Zero;
        public float speed;
        public float acceleration;
        public Int16 trailer_count;
        public Int16 id;

        // These only affect vehicles in TMP
        public bool isTMP;
        public bool isTrailer;

        public TrafficTrailer[] trailers = Array.Empty<TrafficTrailer>();
    }

    public class TrafficData
    {
        public TrafficVehicle[] vehicles = Array.Empty<TrafficVehicle>();
    }

    public enum TrafficLightState
    {
        OFF,
        ORANGETORED,
        RED,
        ORANGETOGREEN = 4,
        GREEN = 8,
        SLEEP = 32,
    }

    public enum GateStates
    {
        CLOSING,
        CLOSED,
        OPENING,
        OPEN
    }

    public enum SemaphoreType
    {
        TRAFFICLIGHT = 1,
        GATE = 2
    }

    public class Semaphore
    {
        public Vector3 position = Vector3.Zero;
        public float cx;
        public float cy;
        public Quaternion rotation = Quaternion.Identity;
        public SemaphoreType type;
        public float time_remaining;
        public int state;
        public int id;
    }

    public class SemaphoreData
    {
        public Semaphore[] semaphores = Array.Empty<Semaphore>();
    }

    public class NavigationEntry
    {
        public ulong nodeUid;
        public float distanceToEnd;
        public float timeToEnd;
    }

    public class NavigationData
    {
        public NavigationEntry[] entries = Array.Empty<NavigationEntry>();
    }
}