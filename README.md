I will rewrite the entire application to be less prone to issues, as well as more modular for plugins etc...

ETA is the end of summer. Keep in mind I have other projects too! (16/6/2023)

### Progress

- [x] Plugin support for UI
  - [x] Implement UI helpers for plugins for consistent style (sv_ttk coming in clutch)
  - [x] Load the plugin canvas
  - [x] Update open plugin on each loop
- [ ] Implement constantly running plugins (currently working on this)
  - [x] Add dynamic tags to PluginInformation (before lanes/steering/game/app update)
  - [ ] Implement UI for toggling different plugins
  - [ ] Depending on needs make it so you can change the execution order
  - [ ] Run all "enabled" plugins on each loop
  - [ ] Make sure that all "mandatory plugins" are enabled (e.g. at least one lane detection model)
- [ ] Implement cross plugin data (to be passed on each plugin update)
- [ ] Remake basic functionality as plugins
  - [ ] Image capture
  - [ ] Lane detection
  - [ ] Controller support
  - [ ] Game support
- [ ] Start adding all other features from LSTR-Development
- [ ] Release v1.0 (yes the branch name is wrong)
- [ ] Future development (now as plugins, YAY)
