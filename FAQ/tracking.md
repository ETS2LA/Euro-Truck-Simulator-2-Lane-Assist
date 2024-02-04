---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-02-04
icon: question
---
!!! Note
Only the crash reporter is present in the application currently. The purpose of this page is to gather feedback on future features. If you have any, please let us know in the feedback panel in the app, or on the discord.
!!!

# Tracking
This page will tell you what we track, how, and where it's stored. 
**Our goal is to be as transparent as possible, especially regarding tracking**.
!!!secondary TLDR
By default all optional settings are off. If you don't touch these settings, no data will ever be saved on the server.
!!!
### Tracking architecture.
There are two types of tracking in the app. 
**Plugins cannot require tracking being enabled, I will not force it on anyone.**
||| Passive

==- [!badge variant="dark" text="Required"] ‎ Passive server pings
This ping is used to determine the amount of currently active users. The app will passively ping the server every 2 minutes.

In the future this ping will also check for responses to feedback or crash reports, and notify the user if there are any.

!!! Note
This ping sends the server your UUID, but it is not stored anywhere. If the server crashes, the UUID is lost.
!!!

==- [!badge variant="ghost" text="Optional"] ‎ Additional information pings
If enabled, it will ping the server with additional information. This includes your FPS and enabled plugins. These are sent along with your UUID, this is to make sure that we don't overlap data.

==-

||| Event driven

==- [!badge variant="ghost" text="Optional"] ‎ Crash reports
If you've enabled the crash reporting, the app will send the entire traceback (anonymized) to the server. This does not include your UUID.

[!badge variant="warning" text="Storage Exception"] ‎ 
This data is sent to a private discord channel for developers. I do not store the data on my server, but it does pass through it.

==- [!badge variant="ghost" text="Optional"] ‎ Feedback
Feedback that is sent through the feedback panel. Just as with the crash reports, this does not include your UUID.

[!badge variant="warning" text="Storage Exception"] ‎ 
This data is sent to a private discord channel for developers. I do not store the data on my server, but it does pass through it.

==-
|||

### How we store data.
Everything collected is stored on my own server. There are no backups online, and nothing leaves my own local network. Any exceptions to this are listed in the architecture section above.

### What is included in the data.
You can see a list of what all the data we collect is used for and means.
**Please note that depending on the tracking options you have selected, not all of this data is gathered. You can see which options enable each data point in the list below.**

==- User UUID
[!badge variant="ghost" text="Passive server pings"] [!badge variant="ghost" text="Additional information pings"]

This is a unique identifier for your computer. The UUID cannot be used to determine anything about your PC, but it is used to make sure we can tell the difference between different machines. In the future you should also be able to use your UUID to log into the web interface to follow your crash reports and feedback requests.

!!! Note
You can check your own UUID by running the following in a console:
```bash
python -c "import uuid; print(uuid.UUID(int=uuid.getnode()))"
```
!!!

==- FPS and / or enabled plugins
[!badge variant="ghost" text="Additional information pings"]

This can be used by us to determine bottlenecks within the app. I also plan on making a public page where you can see the average FPS based on plugin usage, obviously depending on how much data we get.

==- Crash traceback
[!badge variant="ghost" text="Crash reports"]

The crash reporter, if enabled, will send the traceback to us. This is used to determine the most common crashes and to fix them.

!!! Note
These tracebacks are anonymized. This means we for example replace the username with "censored". Though if you use the default install location, it wouldn't be present in the traceback anyway.
!!!
==-

!!! Important
Nothing we collect can be used to identify you, or get information about your PC.
We also do not send any files etc... 

If you want to check the actual code then it is [available on github](https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/blob/main/src/server.py), so we have nothing to hide.
Server code is not open source for multitudes of reasons, one of which obviously being security.
!!!

### What happens if my server crashes, or you don't have an internet connection?
- The app will work as it always has. We will never include anything that would lock the app when the user doesn't have connection to the server.
- Any feature that requires the server specifically will not work.
  - For example, the feedback and crash reports.
- There's going to be a note in the main menu that the server is down.
- The app will keep looking for the server once every 2 minutes.

As for data, the UUIDs relating to the automatic pings will be lost. Most other data is saved on disk, and with the exception of data that is sent at the exact time of the crash, that data will remain even if the server crashes.