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
}