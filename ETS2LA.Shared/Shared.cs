namespace ETS2LA.Shared
{
    public interface IEventBus
    {
        void Subscribe<T>(string topic, Action<T> handler);
        void Unsubscribe<T>(string topic, Action<T> handler);
        void Publish<T>(string topic, T data);
    }

    public interface IPlugin
    {
        void Init(IEventBus bus);
        void Shutdown();
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
}