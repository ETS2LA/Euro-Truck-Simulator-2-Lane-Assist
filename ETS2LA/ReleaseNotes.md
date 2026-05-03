### ETS2LA C# 3.1.14
* ETS2LA will now automatically load game data, including mods, from the currently open game. The loading will begin after you've started loading a profile.
* Removed `Game/Mods` tab from the UI, as it's no longer needed.
* Updated `TruckLib.Models` to latest version, and added support for roads with only left models. These are present in Project Japan, which now works perfectly.
* Refactored the notification system so that it's separate from our UI. Plugins can now listen to notification events from `ETS2LA.Notifications`.

**WARNING:** ETS2LA C# on Linux requires Linux specific SDKs. These can be found on the closed beta Discord, as they aren't yet included in ETS2LA C#.

**IMPORTANT:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/download. This version is not what you're looking for!