using System.Reflection;
using System.Security.Cryptography;

namespace ETS2LA.Shared
{
    public interface IEventBus
    {
        void Subscribe<T>(string topic, Action<T> handler);
        void Unsubscribe<T>(string topic, Action<T> handler);
        void Publish<T>(string topic, T data);
    }

    // Interface that plugins will follow at a minimum
    public interface IPlugin
    {
        bool _IsRunning { get; set; }
        void Init(IEventBus bus);
        void OnEnable();
        void Tick();
        void OnDisable();
        void Shutdown();
    }

    // ETS2LA default plugin class. You can still create your own
    // but please note that it is *highly* recommended to use this as a base.
    public abstract class Plugin : IPlugin
    {
        protected IEventBus? _bus;
        public bool _IsRunning { get; set; } = false;
        public virtual float TickRate => 20.0f;

        public virtual void Init(IEventBus bus) { _bus = bus; }
        public virtual void OnEnable()
        {
            _IsRunning = true;
            Task.Run(() => RunningThread());
        }

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

    [AttributeUsage(AttributeTargets.Assembly)]
    public class PluginInformation : Attribute
    {
        // Required
        public string Name { get; }
        public string Description { get; }

        // Optional
        public string AuthorName { get; set; } = "";
        public string AuthorWebsite { get; set; } = "";
        public string AuthorIcon { get; set; } = "";
        public string[] Tags { get; set; } = Array.Empty<string>();

        public PluginInformation(string name, string description)
        {
            Name = name;
            Description = description;
        }
    }

    // Utility classes
    public class Vector3
    {
        public float X;
        public float Y;
        public float Z;

        public Vector3(float x, float y, float z)
        {
            X = x;
            Y = y;
            Z = z;
        }

        public override string ToString()
        {
            return $"({X}, {Y}, {Z})";
        }

        public static Vector3 Zero => new Vector3(0, 0, 0);
        public static Vector3 One => new Vector3(1, 1, 1);

        public float[] ToArray()
        {
            return new float[] { X, Y, Z };
        }
    }

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

    public class Camera
    {
        public float fov;
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