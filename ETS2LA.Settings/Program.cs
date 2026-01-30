using System.Reflection.Metadata;
using System.Text;
using System.Text.Json;

namespace ETS2LA.Settings
{
    public class SettingsHandler : IDisposable
    {
        readonly string _baseDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "ETS2LA");
        readonly JsonSerializerOptions _jsonOpts = new JsonSerializerOptions {
            WriteIndented = true,
            IncludeFields = true
        };

        // This will disable listener callbacks during save operations.
        // Otherwise saving a file would trigger the listener callback to read it
        // at the same time -> file access conflicts.
        readonly List<string> _savingInProgress = new();

        readonly Dictionary<string, List<ListenerEntry>> _listeners = new(StringComparer.OrdinalIgnoreCase);
        class ListenerEntry
        {
            public Type? DataType;
            public Delegate Callback;
            public ListenerEntry(Type? type, Delegate cb) { DataType = type; Callback = cb; }
        }

        readonly object _sync = new();
        readonly FileSystemWatcher _watcher;

        public SettingsHandler()
        {
            Directory.CreateDirectory(_baseDir);
            _watcher = new FileSystemWatcher(_baseDir)
            {
                NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.CreationTime,
                IncludeSubdirectories = false,
                EnableRaisingEvents = true
            };
            _watcher.Changed += OnFsEvent;
            _watcher.Created += OnFsEvent;
            _watcher.Renamed += OnFsRenamed;
            _watcher.Deleted += OnFsEvent;
        }

        private void VerifyJsonPath(string fileName)
        {
            if (!fileName.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Settings file name must end with .json");
        }

        public bool Save<T>(string fileName, T data)
        {
            VerifyJsonPath(fileName);
            string json = JsonSerializer.Serialize(data, _jsonOpts);

            Directory.CreateDirectory(Path.GetDirectoryName(Path.Combine(_baseDir, fileName))!);
            string target = Path.Combine(_baseDir, fileName);
            string temp = target + ".tmp";

            // Write temp file, then replace the target to avoid lock issues.
            try
            {
                _savingInProgress.Add(fileName);
                File.WriteAllText(temp, json, Encoding.UTF8);
                int retries = 3;
                while (retries-- > 0)
                {
                    try {
                        if (File.Exists(target)) 
                        { 
                            File.Replace(temp, target, null); 
                            break;
                        }
                        else
                        {
                            File.Move(temp, target);
                            break;
                        }
                    } catch (IOException) when (retries > 1) {
                        Thread.Sleep(50);
                    }
                }
                _savingInProgress.Remove(fileName);
            } catch (Exception ex)
            {
                _savingInProgress.Remove(fileName);
                Console.WriteLine($"Failed to save settings file {fileName}: {ex}");
                File.Delete(temp);
                return false;
            }

            // Manually trigger listeners since FS watcher is ignored during save.
            HandleFsChange(target, fileName);
            return true;
        }

        public T Load<T>(string fileName)
        {
            VerifyJsonPath(fileName);
            string path = Path.Combine(_baseDir, fileName);
            if (!File.Exists(path))
            {
                Save(fileName, Activator.CreateInstance<T>());
                return Activator.CreateInstance<T>();
            }

            string json = File.ReadAllText(path, Encoding.UTF8);
            try
            {
                var data = JsonSerializer.Deserialize<T>(json, _jsonOpts);
                return data != null ? data : default!;
            }
            catch (JsonException)
            {
                Console.WriteLine($"Failed to deserialize settings file {fileName}, returning default instance.");
                return Activator.CreateInstance<T>();
            }
        }

        public void RegisterListener<T>(string fileName, Action<T> callback)
        {
            VerifyJsonPath(fileName);
            lock (_sync)
            {
                if (!_listeners.TryGetValue(fileName, out var list))
                {
                    list = new List<ListenerEntry>();
                    _listeners[fileName] = list;
                }
                list.Add(new ListenerEntry(typeof(T), callback));
            }
        }

        public void UnregisterListener(string fileName, Action callback)
        {
            lock (_sync)
            {
                if (_listeners.TryGetValue(fileName, out var list))
                {
                    list.RemoveAll(e => e.DataType == null && e.Callback.Equals(callback));
                    if (list.Count == 0) _listeners.Remove(fileName);
                }
            }
        }

        public void UnregisterListener<T>(string fileName, Action<T> callback)
        {
            lock (_sync)
            {
                if (_listeners.TryGetValue(fileName, out var list))
                {
                    list.RemoveAll(e => e.DataType == typeof(T) && e.Callback.Equals(callback));
                    if (list.Count == 0) _listeners.Remove(fileName);
                }
            }
        }

        // filesystem watcher handlers (debounce by checking actual timestamp change)
        void OnFsEvent(object? sender, FileSystemEventArgs e) => HandleFsChange(e.FullPath, e.Name);
        void OnFsRenamed(object? sender, RenamedEventArgs e) => HandleFsChange(e.FullPath, e.Name);

        void HandleFsChange(string fullPath, string? name)
        {
            if (name == null) return;
            if (_savingInProgress.Contains(name)) return;

            try
            {
                var lastWrite = File.GetLastWriteTimeUtc(fullPath);
                List<ListenerEntry>? entries = _listeners.TryGetValue(name, out var list) ? new List<ListenerEntry>(list) : null;

                if (entries == null) return;

                // read file like this instead of File.ReadAllText to avoid file lock issues
                using var fs = new FileStream(fullPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
                using var sr = new StreamReader(fs, Encoding.UTF8);
                string? json = null;
                json = sr.ReadToEnd();
                foreach (var entry in entries)
                {
                    if (entry.DataType == null)
                    {
                        entry.Callback.DynamicInvoke();
                        continue;
                    }

                    try
                    {
                        var obj = JsonSerializer.Deserialize(json, entry.DataType, _jsonOpts);
                        entry.Callback.DynamicInvoke(obj);
                    }
                    catch
                    {
                        Console.WriteLine($"Failed to deserialize settings file {name} for listener of type {entry.DataType}, skipping callback.");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing filesystem change for {name}: {ex}");
            }
        }

        public void Dispose()
        {
            _watcher?.Dispose();
        }
    }
}