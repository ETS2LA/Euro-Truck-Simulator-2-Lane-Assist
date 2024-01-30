---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: database
---

!!!warning Warning
This page is meant for `developers`
!!!

## Directly usable functions and values
```python
from src.settings import CreateSettings, GetSettings

# Will create (or update) a new setting in the settings file.
CreateSettings(category, name, data) 

# Will get a specific setting from the settings file.
GetSettings(category, name, value=None) 
```

## Description
Provides an interface to read and write settings from the main JSON file.
**Ideally all settings should be stored using this interface.**