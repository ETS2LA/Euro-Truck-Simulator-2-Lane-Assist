using System.Reflection;
using System.Runtime.Loader;

namespace ETS2LA.Backend
{
    // This custom context is necessary, because otherwise loading a plugin
    // assembly keeps that reference for the lifetime of ETS2LA.
    // That prevents us from loading plugins dynamically without a restart
    // and that in turn makes plugin development more difficult.

    // If anyone has a cleaner solution to this problem then please let me
    // know or make a PR, I don't necessarily like having a separate file and
    // class just for this.
    public sealed class PluginLoadContext : AssemblyLoadContext
    {
        private readonly AssemblyDependencyResolver _resolver;
        private readonly string _pluginDirectoryPath;
        private readonly string _mainAssemblyName;

        public PluginLoadContext(string mainAssemblyPath, string pluginDirectoryPath) : base(isCollectible: true)
        {
            _resolver = new AssemblyDependencyResolver(mainAssemblyPath);
            _pluginDirectoryPath = pluginDirectoryPath;
            _mainAssemblyName = Path.GetFileNameWithoutExtension(mainAssemblyPath);
        }

        protected override Assembly? Load(AssemblyName assemblyName)
        {
            var assemblyPath = _resolver.ResolveAssemblyToPath(assemblyName);
            if (assemblyPath != null)
            {
                return LoadFromAssemblyPath(assemblyPath);
            }

            // Try resolving dependencies from the source plugin directory.
            var dependencyName = assemblyName.Name;
            if (!string.IsNullOrWhiteSpace(dependencyName))
            {
                var candidatePath = Path.Combine(_pluginDirectoryPath, dependencyName + ".dll");
                if (File.Exists(candidatePath))
                {
                    return LoadFromAssemblyPath(candidatePath);
                }
            }

            // Keep framework and shared host assemblies in the default context.
            if (ShouldResolveFromDefaultContext(assemblyName.Name))
            {
                var defaultAssembly = AssemblyLoadContext.Default.Assemblies
                    .FirstOrDefault(a => string.Equals(a.GetName().Name, assemblyName.Name, StringComparison.OrdinalIgnoreCase));
                if (defaultAssembly != null)
                {
                    return defaultAssembly;
                }
            }

            return null;
        }

        protected override IntPtr LoadUnmanagedDll(string unmanagedDllName)
        {
            var libraryPath = _resolver.ResolveUnmanagedDllToPath(unmanagedDllName);
            if (libraryPath != null)
            {
                return LoadUnmanagedDllFromPath(libraryPath);
            }

            return IntPtr.Zero;
        }

        private bool ShouldResolveFromDefaultContext(string? assemblyName)
        {
            if (string.IsNullOrWhiteSpace(assemblyName))
            {
                return false;
            }

            // Never bind the main plugin assembly from the default context.
            if (string.Equals(assemblyName, _mainAssemblyName, StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            return assemblyName.StartsWith("System.", StringComparison.OrdinalIgnoreCase)
                || assemblyName.StartsWith("Microsoft.", StringComparison.OrdinalIgnoreCase)
                || assemblyName.StartsWith("ETS2LA.", StringComparison.OrdinalIgnoreCase)
                || string.Equals(assemblyName, "System", StringComparison.OrdinalIgnoreCase)
                || string.Equals(assemblyName, "mscorlib", StringComparison.OrdinalIgnoreCase)
                || string.Equals(assemblyName, "netstandard", StringComparison.OrdinalIgnoreCase);
        }
    }
}