---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: broadcast
---

!!!warning Warning
This page is meant for `developers`
!!!
!!! Note
If the user has not accepted to crash reporting, this file will do nothing.
!!!

## Directly usable functions and values
```python
from src.server import SendCrashReport

# Send a crash report to the discord server (only if the user has accepted crash reporting).
SendCrashReport(type:str, message:str, additional=None)
```

## Description
Will send data my personal server, for now all data forwarded onwards to the discord.
No data is stored yet.