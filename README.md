## ETS2LA C# Rewrite
We're reaching the limits of what we can do on Python, so we've decided to start rewriting ETS2LA in C#. This will improve performance, maintainability, and code quality. This branch is a work in progress, and it's not ready for production use. If you're a developer, then feel free to contribute!

## Building the Project
First download .NET 10 from Microsoft. You can find that [here](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).

Now clone the repository and open the solution file in your preferred IDE. It's recommended to use VS Code, and that's what I'll be using here. Any code editor should work, but the project comes prepackaged with vscode defs.

You can build the project by pressing `F1` and then typing in `.NET: Build`. Code will ask you for which projects to build and you'll want to select `All Projects`. This should build ETS2LA and you'll see a `bin` folder appear in `ETS2LA.Backend/bin` where the compiled files are.

> You don't need to build *everything* all the time, once you've built once you can just build whatever you changed by selecting only that project.

To run ETS2LA the easiest is to open the `Program.cs` file in `ETS2LA.Backend` and press the `>` in the top right hand corner. You can also create your own macros in your IDE of choice to build and run the project on a keypress.

## Contributing
Whatever you contribute please first **fork** the repository and make your changes in your own seperate branch. Once you're done you can open a PR and we'll review it as soon as possible. The rewrite is still in a very early stage so any improvements and contributions are very much welcome!

## Plugin Development
> The 3rd party plugin framework is not yet implemented. You can still develop plugins as their APIs will be identical to official plugins, but we have no way to release them other than copying their files to `Plugins/` in the build folder.

There's a premade C# template in `/.vscode/template/`. You can check the markdown file in that folder to create your own plugin project. Once you've created your plugin you can check below for our main development docs. These will be expanded and moved to `https://docs.ets2la.com` once we get further along in development.

### The Plugin Class
You can customize your plugin class as you see fit, it is still recommended to use the official `Plugin` class instead of creating your own. Below is a list of functions and variables the official class has.
```csharp
public abstract class Plugin : IPlugin
{
    // Used to communicate with other plugins, expanded further later.
    protected IEventBus? _bus;

    // Marks if the plugin Tick thread is currently running.
    public bool _IsRunning { get; set; } = false;

    // Maximum tickrate of the plugin, in ticks per second.
    public virtual float TickRate => 20.0f;

    // Called when the plugin is initially loaded.
    // Please make sure to call `base.Init(bus)` if you override this function.
    public virtual void Init(IEventBus bus) {}

    // Called when the plugin is enabled, please also call `base.OnEnable()` if you 
    // override this function or the tick thread will not start.
    public virtual void OnEnable() {}

    // Protected function that cannot be overwritten. It runs the main tick loop
    // at the tickrate you selected.
    protected void RunningThread() {}

    // Called every tick, think of it like the Update() function in Unity.
    public virtual void Tick() {}

    // Called when the plugin is disabled, please also call `base.OnDisable()` if you
    // override this function or the tick thread will not stop.
    public virtual void OnDisable() {}

    // Called when the plugin is unloaded, use this to clean up any resources.
    public virtual void Shutdown() {}
}
```

### Inter Plugin communication
All communication in ETS2LA is handled via the event bus. You can subscribe to events that other plugins fire, and you can also fire your own events. Below is an example of how to use the event bus.

> The event bus works even if the plugin is disabled! If you do anything that could count as "enabled" behaviour, then please remember to check the `_IsRunning` variable in your callback before the code.

```csharp
// Provider will call .Publish to fire an event to all subscribers.
// You have to include the type of data you're sending as a generic parameter.
_bus.Publish<float>("ExampleProvider.CurMicroseconds", System.DateTime.Now.Microsecond);

// And now a subscriber can listen to that event via a callback function.
_bus.Subscribe<float>("ExampleProvider.CurMicroseconds", OnCurMicroseconds);

void OnCurMicroseconds(float microseconds)
{
    Console.WriteLine($"Current microseconds: {microseconds}");
}
```
These events run almost instantly accross all plugins. You can send as large of a data as you want, as these events only pass memory addresses around. Just be careful about editing data!

### Accessing Game Data
> TODO: Write telemetry and ETS2LA SDK reader plugins.