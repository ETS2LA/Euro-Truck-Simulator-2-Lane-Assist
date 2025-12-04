using ETS2LA.Shared;

namespace ETS2LA.Backend
{
    public class EventBus : IEventBus
    {
        private static readonly Dictionary<string, List<Delegate>> _subscribers = new();

        public void Subscribe<T>(string topic, Action<T> handler)
        {
            if (!_subscribers.ContainsKey(topic))
            {
                _subscribers[topic] = new List<Delegate>();
            }
            _subscribers[topic].Add(handler);
        }

        public void Unsubscribe<T>(string topic, Action<T> handler)
        {
            if (_subscribers.ContainsKey(topic))
            {
                _subscribers[topic].Remove(handler);
            }
        }

        public void Publish<T>(string topic, T data)
        {
            if (_subscribers.ContainsKey(topic))
            {
                foreach (var handler in _subscribers[topic])
                {
                    if (handler is Action<T> action)
                    {
                        action.Invoke(data);
                    }
                }
            }
        }
    }
}