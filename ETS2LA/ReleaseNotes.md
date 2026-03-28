### ETS2LA C# 3.1.7
* ETS2LA C# now supports the new SDKs from the main Python version. You can now use ETS2LA C# with ETS2 1.58.
* These new SDKs are also supported on Linux, you can find linux binaries in the closed beta discord announcements.
* Removed `ETS2LASDK` and `ControlsSDK` plugins. These are now handled by `ETS2LA.Game.SDK` and `ETS2LA.Game.Output.GameOutput` respectively.
* Multiple plugins can now send control values at the same time, and these will be weighed together. You can now have one plugin for ACC, and one for AEB, for instance.
* Removed `GameTelemetry` plugin in favor of `ETS2LA.Telemetry`, which doesn't depend on the plugin backend and is always running.

**WARN:** ETS2LA C# cannot yet use the new SDK that the Python version uses. You can find the latest version of the old SDK [on GitHub](https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist/tree/ef17194f94214f3ababc619cff12ff74e0729574/ETS2LA/Assets/DLLs/1.58).

**NOTE:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/downloads. This version is not what you're looking for!