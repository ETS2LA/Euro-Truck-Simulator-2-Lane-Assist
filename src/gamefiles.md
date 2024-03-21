---
authors: 
  - name: Glas42
    link: https://github.com/Glas42
    avatar: https://avatars.githubusercontent.com/u/145870870?v=4
date: 2024-3-21
icon: database
---

!!!warning Warning
This page is meant for `developers`
!!!

## How to use
```python
import src.gamefiles as gamefiles

"""Reads the controls file of the selected game with the most recent usedprofile."""
ReadProfileControlsFile(str)
"""Reads the config_local file of the selected game with the most recent usedprofile."""
ReadProfileConfigFile(str)
"""Reads the global controls file of the selected game."""
ReadGlobalControlsFile(str)
"""Reads the global config file of the selected game."""
ReadGlobalConfigFile(str)
"""Reads the game log of the selected game."""
ReadGameLogFile(str)
```

## Description
Is able to read different files like controls or configs from the game files and returns the content of the file.