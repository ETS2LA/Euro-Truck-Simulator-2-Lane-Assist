ETA is the end of summer. Keep in mind I have other projects too! (16/6/2023)

> Right now you can try out the new plugin based UI and go through the first time setup. Next up is constantly running plugins!

### Progress

- [x] Plugin support for UI
  - [x] Implement UI helpers for plugins for consistent style (sv_ttk coming in clutch)
  - [x] Load the plugin canvas
  - [x] Update open plugin on each loop
  - [x] Create "plugins.FirstTimeSetup" as a test
- [x] Implement constantly running plugins (currently working on this)
  - [x] Add dynamic tags to PluginInformation (before lanes/steering/game/app update)
  - [x] Implement UI for toggling different plugins
  - [ ] Depending on needs make it so you can change the execution order
  - [x] Run all "enabled" plugins on each loop
  - [x] Make sure that many plugins of the same "category" are not enabled (for example 2 lane detection models)
- [x] Implement cross plugin data (to be passed on each plugin update)
- [x] Remake basic functionality as plugins
  - [x] Image capture
  - [x] Lane detection (WOO IT WORKS)
  - [x] Steering
  - [x] Controller support
  - [ ] Game support (API) -> This is going to be done by [Cloud](https://github.com/Cloud-121) at some point!
- [ ] Start adding all other features from LSTR-Development
- [ ] Release v1.0 (yes the branch name is wrong)
- [ ] Future development (now as plugins, YAY)

### Goals

Why did I suddenly start rewriting the app instead of focusing on new features? 
Well the most important goal is to make a cohesive and easy to use codebase. The current LSTR-Development version is full of spaghetti code that even I can't understand after half a year.
With the new rewrite I'm aiming to make everything as modular as possible so that new features can be easily implemented. In essence: 
```
Development goals for v1.0 :
- Create a cohesive codebase that is very easy to add to
- Implement all possible features as plugins
  - Allow users to create these plugins by creating a documentation site
  - Allow users to download plugins automatically from github.
- Implement superior performance by optimizing screen capture and decoupling the UI from the rest of the application
- Implement some sort of OSD, so that changing settings on the fly is as easy as possible.
- Create a trailer before release and create a new and improved downloader (already done for LSTR-Development).
- Have the first time user experience improved.
```
All this is born with one goal in mind; have the community help with development.

### Can I help. How about developing plugins?
Well v1.0 is still under **heavy** development, but the main UI framework is there.

If you want to help with development, then the easiest way is to reach out to me on discord (@tumppi066) and we'll talk about the easiest way to get you involved!
