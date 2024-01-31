---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-31
icon: stack
tags: 
  - tutorial
title: Plugin Creation
---

### Introduction
This tutorial page will run you through the creation of a simple plugin that will output the current value of the in game time. 
We will also be sending information to the game, and reading a control value from the user.

[!badge variant="warning" text="This page is WIP and not yet complete!"]

### The plugin framework
The plugin framework of ETS2LA is fairly simple. All plugin live in the /plugins folder, these are loaded by the program when it starts up.

Here's some stuff to note on the file and code structure:
+++ File structure

```
plugins
├─── plugin
│   ├─── main.py
│   ├─── installer.py
│   ├─── plugin.md
│   ├─── docs.md
```

==- [!badge variant="dark" text="Required"] ‎ main.py
This is the main file of the plugin. It will be imported once the program starts up. 
!!! Note
You can obviously have other files, but everything must start or be imported from main.py. More on this in the code structure section.
!!!

==- [!badge variant="dark" text="Required"] ‎ installer.py
This file is used when the application discovers the plugin for the first time. It usually contains code for installing pip packages, this is included in the example installer.py.

==- [!badge variant="ghost" text="Optional"] ‎ plugin.md
This file contains the information displayed on the left side of this page. It is written in markdown, and is parsed by the application. 
**The name of this file must match the name of the folder it's in.**
!!! Note
Documentation can be found on the [retype website](https://retype.com).
!!!

==- [!badge variant="ghost" text="Optional"] ‎ docs.md
This file on the other hand contains information for developers, it will be opened by the button located in the plugin.md file. This is also included in the example plugin.
==-

+++ Code structure

The program includes some predefined functions. These are used by the main program loop to send extra information to the plugin.

==- [!badge variant="dark" text="Required"] ‎ `PluginInfo = PluginInformation()`
This is the class that contains information about the plugin. It is used by the program to display information about the plugin in the plugin manager.

**The plugin example will contain almost everything you need.**

!!! Note
You can check the current state of the file [on the documentation page](https://wiki.tumppi066.fi/docs/plugins/plugin.html).
!!!

==- [!badge variant="dark" text="Required"] ‎ `plugin(data)`
**This is the main function of the plugin.**
It will be run every frame, and the current program data `dictionary` will be passed on to it. 
!!! Note
It is paramount that you return the `data` variable! 
Don't worry, the program will shout at you if you forgot :+1:
!!!

==- [!badge variant="ghost" text="Optional"] ‎ `onEnable()`
This function is called in two cases:

1. When the plugin is enabled and loaded at startup
2. When the plugin is enabled through the plugin manager

This is useful if you for example have to do some heavy calculations. We don't want those calculations unnecessarily running when starting up. Thus they will run only when the plugin is actually enabled.

==- [!badge variant="ghost" text="Optional"] ‎ `onDisable()`
This function is called when the plugin is disabled. This is useful for cleaning up any resources that the plugin might have used.


==- [!badge variant="ghost" text="Optional"] ‎ `class UI()`
This class is used to create UI for the plugin. We will be using this later on, and it will be explained in more detail then.


==-

+++