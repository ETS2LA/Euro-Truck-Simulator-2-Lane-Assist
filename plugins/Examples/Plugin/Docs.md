---
# https://retype.com/configuration/page/
# please also see the docs for components 
# https://retype.com/components/alert/
authors: 
  - name: Retype
    link: https://retype.com/configuration/page/#visibility
    avatar: https://retype.com/static/retype-logo-dark.svg
date: 2024-1-30
icon: stack
tags: 
  - documentation
---
!!!warning Warning
This page is meant for `developers`
!!!

## Data variable usage
The plugin will use the following data variable values:
=== data/the/path/to/your/variable
The description of the variable

=== data/another/variable
The description of another variable

===

### Example
Copied from the BetterCamScreenCapture plugin:
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
**None / PLEASE FILL IN**