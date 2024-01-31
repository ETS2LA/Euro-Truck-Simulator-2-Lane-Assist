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
=== data/frame
The cropped image frame defined by the settings.

=== data/frameFull
The full image from the display.

=== data/frameOriginal
The original image. THIS SHOULD NOT BE EDITED!

===

### Example

```python
import cv2
def plugin(data):
    frame = data["frame"]
    frameFull = data["frameFull"]
    frameOriginal = data["frameOriginal"] # Frame original should not be edited!

    # Most plugins will edit the frame value for the future. This is because the ShowImage plugin will show the final frame value.
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Make it grayscale for example

    # Return the data variable
    data["frame"] = frame
    return data
```


## Directly usable functions and values
**None**