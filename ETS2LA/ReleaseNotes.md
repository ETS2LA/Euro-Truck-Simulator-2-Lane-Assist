### ETS2LA C# 3.1.8
* Added a new `Data` section in the settings. This section has a new `Data Fidelity` setting that control how much of the data we have available to us we actually load in. `Extreme` requires at least 16gb of RAM, base game ETS2 1.58 on `Extreme` uses at least **9gb** of RAM. These changes will be reflected in the internal visualization. A change of this variable requires a restart of ETS2LA.
* Updated `TruckLib` to it's latest version. Threaded zip loading and fixed mod discovery on Linux in `ETS2LA.Game`.
* ETS2LA C# can now read map data for ProMods, out of ~1300 sectors, 50 fail to load (~3.85%). These are due to out of date sector versions we don't support.
* ETS2LA C# should now also be able to read *most* map mods. 

**WARNING:** ETS2LA C# on Linux requires Linux specific SDKs. These can be found on the closed beta Discord, as they aren't yet included in ETS2LA C#.

**IMPORTANT:** If you're not in the ETS2LA beta program, please take a look at https://ets2la.com/downloads. This version is not what you're looking for!