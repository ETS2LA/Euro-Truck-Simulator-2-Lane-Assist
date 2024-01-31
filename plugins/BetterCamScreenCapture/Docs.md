---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: gear
visibility: hidden
tags:
  - documentation
---

!!!warning Warning
This page is meant for `developers`
!!!
## Data variable usage
The plugin will use the following data variable values:
```python
def plugin(data):
    data["frame"] # The cropped image frame defined by the settings.
    data["frameFull"] # The full image from the display.
    data["frameOriginal"] # The original image. THIS SHOULD NOT BE EDITED!
```

## Directly usable functions and values
**None**