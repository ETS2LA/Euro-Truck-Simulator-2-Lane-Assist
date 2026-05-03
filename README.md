## ETS2LA C# Rewrite
We're reaching the limits of what we can do on Python, so we've decided to start rewriting ETS2LA in C#. This will improve performance, maintainability, and code quality. This branch is a work in progress, and it's not ready for production use. If you're a developer, then feel free to contribute!

## Building the Project
First download .NET 10 from Microsoft. You can find that [here](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).

Now clone the repository and open the solution file in your preferred IDE. It's recommended to use VSCode, and that's what I'll be using here. Any code editor should work, but the project comes prepackaged with VSCode defs. For VSCode you should download the `C# Dev Kit` extension, other IDEs should have their own equivalent extensions.

You can build the project by pressing `F1` and then typing in `.NET: Build`. Code will ask you for projects to build and you'll want to select `All Projects`. This should build ETS2LA and you'll see a `bin` folder appear in `ETS2LA.UI/bin` where the compiled files are.

> You don't need to build *everything* all the time, once you've built once you can just build whatever you changed by selecting only that project.

To run ETS2LA the easiest is to open any `.cs` file in `ETS2LA.UI` and press the run arrow `>` in the top right hand corner. You can also create your own macros in your IDE of choice to build and run the project on a keypress.

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
    // Used to describe the plugin. Name, author etc...
    public abstract PluginInformation Info { get; }

    // Used to communicate with the window, for example sending notifications.
    protected INotificationHandler? _window;

    // Marks if the plugin Tick thread is currently running.
    public bool _IsRunning { get; set; } = false;

    // Maximum tickrate of the plugin, in ticks per second.
    public virtual float TickRate => 20.0f;

    // Called when the plugin is initially loaded.
    // Please make sure to call `base.Init(bus)` if you override this function.
    public virtual void Init() {}

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

### Logging
ETS2LA uses `Serilog` for logging, but we still package our own logging wrapper for ease of use and consistency in imports. You can use the `Logger` class from `ETS2LA.Logging`, below is an example of how to use it:
```csharp
using ETS2LA.Logging;

Logger.Debug("This is a debug message.");
Logger.Info("This is an info message.");
Logger.Warning("This is a warning message.");
Logger.Error("This is an error message.");
Logger.Fatal(new Exception("Example exception"), "This is a fatal message with an exception.");
```
This will log messages to both the console and to log files in the AppData folder (**TODO**).

### Settings Handler
ETS2LA comes with a built in settings handler that you can use to save and load settings for your plugin. The settings are stored in JSON files in the user's AppData folder. Below is an example:
```csharp
using System;
using ETS2LA.Settings;

[Serializable] // don't forget Serializable!
class MySettings
{
    public int ExampleValue = 42;
}

...

public override void OnEnable()
{
    base.OnEnable();

    // Setup the settings handler
    _settingsHandler = new SettingsHandler();

    // Then load initial settings. This will automatically
    // generate the file if it doesn't exist yet, so no need to
    // worry about null checks.
    _settings = _settingsHandler.Load<MySettings>(_settingsFilename);
    
    // We can also register a listener to get notified when the settings change
    // on disk. This is much cheaper than continuously polling for changes with .Load.
    _settingsHandler.RegisterListener<MySettings>(_settingsFilename, OnSettingsChanged);

    // Reading and writing works as you'd expect.
    Console.WriteLine($"ExampleProvider loaded setting ExampleValue = {_settings.ExampleValue}");
    _settings.ExampleValue += 1; // This doesn't automatically save to disk!

    // To save you can call .Save on the settings handler. That will
    // flush the current state of the _settings object to disk.
    _settingsHandler.Save<MySettings>(_settingsFilename, _settings);
}

...

private void OnSettingsChanged(MySettings data)
{
    Console.WriteLine($"ExampleProvider detected settings change: ExampleValue = {data.ExampleValue}");
    _settings = data;
}
```

On disk this will create a file at `%AppData%/ETS2LA/_settingsFilename.json` with the following content:
```json
{
    "ExampleValue": 42
}
```
Users can manually edit the file if they want to change settings outside of ETS2LA. For example if with some settings your plugin is broken, they can manually change it.

**NOTE:** Please do not spam the `Save()` function. It is recommended to only save it when a plugin gets disabled or unloaded (or a user changes a setting). You would be spending unnecessary resources and disk writes if you save every frame.

Additionally ETS2LA provides global settings under `ETS2LA.Settings.Global`. These are shared between all plugins and the main window. **If your setting is found here, then use it instead of your own manager!** This way users only have to change a setting once for all plugins to apply it. Below is an example of how to use global settings, this example uses the `AssistanceSettings` class for driving assist settings.
```csharp
using ETS2LA.Settings.Global;
AssistanceSettings assistanceSettings = AssistanceSettings.Current;
Console.WriteLine($"Following Distance: {assistanceSettings.FollowingDistance}");
assistanceSettings.FollowingDistance = FollowingDistanceOption.Near;
Console.WriteLine($"Following Distance is now: {assistanceSettings.FollowingDistance}");
```
Notice that you do not need to call `.Save()` on global settings. Since these are shared between all plugins, any changes are automatically received by them. The backend will handle saving when necessary. **REMEMBER:** If you change a global setting, please notify the user, either via a notification or some other way. They should always know when a setting changes (and ideally it never should without a user's action).

### Inter-Plugin communication
All communication in ETS2LA is handled via the event bus. You can subscribe to events that other plugins fire, and you can also fire your own events. Below is an example of how to use the event bus.

> The event bus works even if the plugin is disabled! If you do anything that could count as "enabled" behaviour, then please remember to check the `_IsRunning` variable in your callback before the code.

```csharp
// Provider will call .Publish to fire an event to all subscribers.
// You have to include the type of data you're sending as a generic parameter.
Events.Current.Publish<float>("ExampleProvider.CurMicroseconds", System.DateTime.Now.Microsecond);

// And now a subscriber can listen to that event via a callback function.
Events.Current.Subscribe<float>("ExampleProvider.CurMicroseconds", OnCurMicroseconds);

void OnCurMicroseconds(float microseconds)
{
    Console.WriteLine($"Current microseconds: {microseconds}");
}
```
These events run almost instantly accross all plugins. You can send as large of a data as you want, as these events only pass memory addresses around. Just be careful about editing data!

### Accessing Game Telemetry
You can listen to the game telemetry using the `GameTelemetry`'s event. This event will be called at 60Hz with the latest telemetry from the game. Please note that the telemetry might not change every frame, as the game might be running at under 60FPS.

> Please do not do heavy calculations in the callback to avoid slowdowns, ideally you should copy the data to a variable, and use that variable in the `Tick()` function or other threads.
```csharp
GameTelemetryData _latestTelemetry;
Events.Current.Subscribe<GameTelemetryData>(GameTelemetry.Current.EventString, OnGameTelemetryData);

...

private void OnGameTelemetryData(GameTelemetryData data)
{
    _latestTelemetry = data;
}

public override void Tick()
{
    if (!_IsRunning) return;

    // Use _latestTelemetry here
    Console.WriteLine($"Truck speed: {_latestTelemetry.truckFloat.speed} m/s");
}
```

Reading ets2la_plugin information can be done like so. Just replace `CameraProvider` with whatever available data structure you want to read.
```csharp
using ETS2LA.Game.SDK;

CameraData _latestCamera;
Events.Current.Subscribe<CameraData>(CameraProvider.Current.EventString, OnCameraData);

private void OnCameraData(CameraData data)
{
    _latestCamera = data;
}

public override void Tick()
{
    if (!_IsRunning) return;

    // Use _latestCamera here
    Console.WriteLine($"Camera FOV: {_latestCamera.fov}");
    Vector3 eulerAngles = _latestCamera.rotation.ToEuler();
    Console.WriteLine($"Camera Rotation: ({eulerAngles.X}, {eulerAngles.Y}, {eulerAngles.Z})");
} 
```
The camera rotation is a quaternion by default, so we provide the `.ToEuler()` method to convert it back to human readable euler angles.

Current the available ETS2LASDK data structures are:
- (`ETS2LA.Game.SDK.`)`CameraProvider` (`CameraData`)
- (`ETS2LA.Game.SDK.`)`TrafficProvider` (`TrafficData`)
- (`ETS2LA.Game.SDK.`)`SemaphoresProvider` (`SemaphoreData`)
- (`ETS2LA.Game.SDK.`)`NavigationProvider` (`NavigationData`)

### Accessing Game Data
Game data is accessible through ETS2LA's `ApplicationState`. As long as a game is running and ETS2LA can properly determine where that game is located, you can get the `MapData` instance by calling.
```csharp
using ETS2LA.State;

var mapData = ApplicationState.Current.RunningGame.GetMapData();
if (mapData == null)
    return;

// Now you can use this instance however you want.
// NOTE: You only need to run this once, you get a pointer to the instance
//       instead of a copy of it. That would take too much RAM.
```
There's *a lot* of data here, and getting used to how it's formatted is on you. That said you can find examples and documentation in [sk-zk's TruckLib Documentation](https://sk-zk.github.io/trucklib/master/docs/introduction.html). Note that ETS2LA includes several helpers and wrappers on top of TruckLib to make working with this data easier. You should take a look at the source code of `ETS2LA.Game.Data` to see how it all fits together.

### Sending Controls to the Game
Much like the telemetry, ETS2LA includes a built in method for sending controls to the game. This is exposed at `ETS2LA.Game.Output` as the `GameOutput` class. This class will handle different methods of sending information to the game, as well as weighing different plugins' outputs together.

```csharp
using ETS2LA.Game.Output;
using ETS2LA.Backend.Events;

Events.Current.Publish<ControlEvent>(GameOutput.Current.EventString, {
  new ControlChannel{
    Id = "MyControlChannel",
    Timeout = 0.2f  // After how much inactivity is the channel cleared.
                    // Manual clearing with an empty ControlVariables.
  },
  new ControlProperties{
    BooleanType = ControlBooleanType.TrueToToggle,
    Weight = 0.5f
  },
  new ControlVariables{ // Check this class for a list of all available variables.
    light = true,    // TrueToToggle means ETS2LA will automatically toggle this off
                     // to simulate a button press.
    aforward = 0.67f // The ControlProperties array defines how much this input is weighed
                     // when calculating the average of all ControlChannels.
    // We use aforward and abackward, as that's what the game does.
    // Internally these are averaged out into an "acceleration" variable.
  }
});
```
In addition to normal controls, we've also implemented force feedback support via Windows.Gaming.Input. It works similarly to `ETS2LA.Game.Output`, but the event name is `ForceFeedback.Output`. For a full list of supported wheels, please check [the Windows docs](https://learn.microsoft.com/en-us/uwp/api/windows.gaming.input.racingwheel?view=winrt-26100#remarks), other wheels are not supported at this time.

**Warning:** This system is not yet generalized in the way `ETS2LA.Game.Output` is, and it will change in the future before release. If you don't absolutely need to use FFB, then it is recommended to wait.

### Creating and Listening to User Controls (Keybinds)
ETS2LA provides a built in `ControlsBackend` that you can use to create user configurable keybinds for your plugin. These keybinds can be buttons or axes from any connected joystick, gamepad, or keyboard. Below is an example of how to create and listen to a control.

```csharp
using ETS2LA.Controls;

public ControlDefinition ExampleControl = new ControlDefinition
{
    Id = "ExampleConsumer.ExampleControl", // Never change ID once set!
    Name = "Example Control",
    Description = "An example control that outputs a float value.",
    DefaultKeybind = "K", // You can set any key(!) here, leaving as blank will make it unbound by default.
    Type = ControlType.Float // ControlType.Boolean is also available, note that keys and buttons can be
                             // bound to ControlType.Float as well, giving a value of 0.0f or 1.0f.
                             // Similarly axes can be bound to ControlType.Boolean, giving true/false values
                             // based on a threshold (0.5f).
};

public override void Init()
{
    base.Init();
    ControlsBackend.Current.RegisterControl(ExampleControl);
    ControlsBackend.Current.On(ExampleControl.Id, OnExampleControlChanged);
}

private void OnExampleControlChanged(object sender, ControlChangeEventArgs e)
{
    float value = (float)e.NewValue; // Remember to cast to your type (return is `object`)
}
```
Additionally ETS2LA comes with it's own control system through `ApplicationState`. You can directly listen to the following variables without ever having to work with this control system:
- DesiredSteeringLevel - *None, LKAS, Full*
- PauseSteeringAssist - *Indicates if you should not send steering output*
- DesiredLongitudinalLevel - *None, AEB, ACC*
- PauseLongitudinalAssist - *Indicates if you should not send longitudinal output*
- DesiredSpeed - *The speed the user wants to drive at in SI units* (m/s)
- DisplayUnits - *The units to use for displaying speed (metric/imperial/scientific)*

This class also includes helper methods for converting between units. You can find the control scheme these variables follow at https://docs.ets2la.com.

### Sending notifications
You can send notifications using `NotificationHandler.Current` from `ETS2LA.Notifications`. Below is an example of how to use it:
```csharp
using ETS2LA.Notifications;

// Static notification
NotificationHandler.Current.SendNotification(new Notification
{
    Id = "MainWindow.TransparencyChanged", // Always set a unique ID for your notification
    Title = "Transparency",
    Content = this.Opacity < 1.0 ? "Enabled" : "Disabled",
    CloseAfter = 2.0f, // Defines how long until the notification auto 
                       // closes, 0 = never -> will show a close button
    Level = this.Opacity < 1.0 
            ? NotificationLevel.Success  // Internally uses Huskui.GrowlItem, so use the 
            : NotificationLevel.Danger   // NotificationLevel enum, included in ETS2LA.Shared.
});

// Dynamic notification (call ShowNotification repeatedly to update)
NotificationHandler.Current.SendNotification(new Notification
{
    Id = "ExampleConsumer.Speed",
    Title = "Truck Speed",
    Content = $"{speed:F2} km/h",
    Level = NotificationLevel.Information,
    Progress = speed / (100 / 3.6f) * 100f, // Progress is from 0 to 100!
    IsProgressIndeterminate = false, // Used when a process is doing something
                                     // without knowing how long it will take.
    CloseAfter = 0 // Always set to 0 unless you want ETS2LA to show
                   // a progress bar for the remaining time. That progress
                   // bar will interfere with anything you set!
});
```
These notification events can also be consumed from said `NotificationHandler`. This allows you to create custom UI elements that react to notifications. Just don't go overboard, as these events are not invoked in a separate thread, and doing heavy calculations in the callback will cause stutters.

### Playing Audio
ETS2LA provides `ETS2LA.Audio` for playing audio. You can use it to play any sound files supported by `NAudio`. Below is an example how to use it:
```csharp
using ETS2LA.Audio;
AudioHandler.Current.Queue("Assets/Sounds/prompt.mp3");
```
> [!NOTE]
> If you need any new features for audio playback, please send us a message on Discord or create an issue / PR on GitHub. Audio playback is extremely barebones and hasn't been thought through yet!

## Acknowledgements
- [SCS Software](https://scssoft.com) - For making Euro Truck Simulator 2 and American Truck Simulator.
- [ts-map](https://github.com/dariowouters/ts-map) and [maps](https://github.com/truckermudgeon/maps) - For their help and examples in parsing SCS map files, and rendering a usable map.