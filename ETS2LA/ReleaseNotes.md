### ETS2LA C# 3.1.2
* Added support for Linux. Currently `ETS2LA.AR` and `ETS2LA.Controls` is disabled on Linux, and plugins can't connect to the SDK yet. This will be improved upon in future releases, for now just getting C# booting on Linux is a good first step.
* Renamed `ControlHandler` to `ControlsBackend` as it changes between platforms. Windows' backend implementation has been renamed to `SharpDXControlsBackend`, Linux' backend is not yet implemented.

**NOTE:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/downloads. This version is not what you're looking for!