---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-02-04
icon: question
---
!!! Note
Nothing in this page is implemented yet, this page is being used to gather ideas and feedback.  
!!!

# Tracking
This page will tell you what we track, how, and where it's stored. 
**Our goal is to be as transparent as possible, especially regarding tracking**.

### Data
!!! Important
Nothing we collect can be used to identify you, or get information about your PC.
We also do not send any files etc... 

If you want to check the actual code then it is available on github, so we have nothing to hide.
Server code is not open source for multitudes of reasons, one of which obviously being security.
!!!
This includes all the data the app will ever collect. It will include the trackers that use each variable, you can then enable and disable the trackers to your choosing.
==- User UUID
This is a unique identifier for your computer. The UUID cannot be used to determine anything about your PC, but it is used to make sure we can tell the difference between different machines.
You can also use your UUID to log into the web interface to follow your crash reports and feedback requests.
!!! Note
You can check your own UUID by running the following in a console:
```bash
python -c "import uuid; print(uuid.UUID(int=uuid.getnode()))"
```
!!!
==- FPS and or enabled plugins
This can be used by us to determine bottlenecks within the app. I also plan on making a public page where you can see the average FPS based on plugin usage, obviously depending on how much data we get.
==- Crash traceback
The crash reporter, if enabled, will send the traceback to us. This is used to determine the most common crashes and to fix them.
==-

### Tracking architecture
There are two types of tracking in the app. 
||| Passive
==- Ping the server
This ping is used to determine the amount of currently active users. The app will passively ping the server every 2 minutes.
==-
||| Event driven
==- Crash reports
If you've enabled the crash reporting, the app will send the entire traceback (anonymized) to the server. This does not include your UUID, so it cannot even be correlated to any feedback.
==-
|||
### How we store data.
I store all stored data on my server. It is stored in a secure format, where only I can access it.