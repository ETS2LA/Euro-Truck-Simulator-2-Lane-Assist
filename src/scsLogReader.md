---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: checklist
title: SCS Log Reader
---

!!!warning Warning
This page is meant for `developers`
!!!
!!! Note
Development of this file is still in progress... In the future we might automatically detect the log entries. 
For now it's all dumped to the `log` data entry.
!!!

## Directly usable functions and values
```python
def plugin(data):
    data["log"] # Includes the entire log file. Only updated when the file is updated.
```

## Description
Listens to the SCS log file and updates the `log` data entry when the file is updated.