---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
date: 2024-3-16
icon: checklist
tags: 
  - tutorial
---

# How to Run a Debug
!!!danger NOTICE
Please do not use debug if you are not told to do so by helpers or developers.
!!!
Running debug can help the developers and helpers debug your app and figure out what is wrong. It is very easy to run debug on your app.

## Check If You have an Old Installer
To check if you have an outdated installer, go to the directory where you have your app installed. This is the directory which has run.bat.

If you have the "menu.bat" file, you have the newer installer version.
If you do not have that, you have the old installer version.

## Verify the Support Bot is Operational
!!! Note
If you have an old installer version, you can skip this step and go to "Running Debug With an Old Installer" to run debug.
!!!

If you are using a new installer version, it will matter wether the supoport bot is working or not. You can still run debug without the support bot though.

Ask your helper or developer if the support bot is working.
If the bot is working, skip to the "Running Debug With a New Installer (With Support Bot)".
If the bot is not working, go to "Running Debug With an New Installer (Without Support Bot)".

## Running Debug With an Old Installer
If you have an old installer, go to the directory where you have your app installed. This is the directory which has run.bat. Here you will find a file called "debug.bat".
Simply run it like you would run.bat. When its done, a file called "debug.txt" will be created. Drag and drop this file into the Discord chat. This will allow your helper/developer to diagnose your app.

## Running Debug With a New Installer (With Support Bot)
If you have a new installer and you have verified that the bot is operational, open the "menu.bat" file. Press the "Debug" button. This will open a window that shows you your debug information. Click the "Send Debug Data" option. once the debug is sent, click close oj the dialog. The debug information will be sent to your helper/developer in a private Discord channel. This data is not stored anywhere external. Find more info about how we use data [here](https://wiki.tumppi066.fi/faq/tracking/).


## Running Debug With an New Installer (Without Support Bot)
If you have a new installer and the support bot is down, open the "menu.bat" file. Press the "Debug" button. This will open a window that shows you your debug information. Click the "Send Debug Data" option. once the debug is sent, click close on the dialog. The debug data is now copied to your clipboard. You have 2 options:
==- Paste it into your Discord chat
Simply just go into the Discord chat and paste the debug data.
==- Copy it to a file and send it to your helper/developer
Create a new text file and paste the debug data into it. Then send it to your helper/developer.
==-

!!!success Thats It!
You have successfully ran debug. Thanks for helping us out! Now just wait for your helper/developer to finish diagnosing your app and then they will assist you in fixing it.
!!!