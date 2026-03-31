### ETS2LA C# 3.1.9
* `ETS2LA.Overlay` now uses the same window rendering code for all windows, instead of two separate systems for internal and plugin windows.
* `OverlayHandler.RegisterWindow` now accepts a second `Action` for rendering context menus. Currently in use by the `Console` window to provide additional options as an example.
* `ETS2LA.Overlay` `WindowDefinition` now provides an `Alpha` variable to control the background's transparency. It also provides a `NoWindow` variable, for plugins who want to render their window entirely by themselves. This environment still supports ImGui, but doesn't have ETS2LA's automatic window handling.
* Added the ability to open previously closed windows. This is available in interaction mode, and it can control all windows, including those made by plugins. 
* Added DPI awareness to `ETS2LA.Overlay`. The overlay will now scale according to the system DPI settings. This is especially useful for 4K displays.
* Added a new `DemoWindow` to the overlay, this is built in to ImGui but I've now wrapped it in our windowing system.
* Fixed some old label text and removed redundant code that was left in.

**WARNING:** ETS2LA C# on Linux requires Linux specific SDKs. These can be found on the closed beta Discord, as they aren't yet included in ETS2LA C#.

**IMPORTANT:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/downloads. This version is not what you're looking for!