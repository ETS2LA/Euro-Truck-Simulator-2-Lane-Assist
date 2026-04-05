### ETS2LA C# 3.1.10
* Added `Unload` and `Reload` buttons to the manager UI, allowing plugin developers to reload their plugins without restarting ETS2LA.
* Build workflow improvements, builds are now also checked in PRs.
* Implemented `ETS2LA.State.ApplicationState` for handling user control inputs globally. Plugins can read the current state without having to figure out control parsing themselves.
* Added a new overlay window for the current state.
* `ETS2LA.Controls` now supports hats, as well as has improved control detection on Linux.

**WARNING:** ETS2LA C# on Linux requires Linux specific SDKs. These can be found on the closed beta Discord, as they aren't yet included in ETS2LA C#.

**IMPORTANT:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/downloads. This version is not what you're looking for!