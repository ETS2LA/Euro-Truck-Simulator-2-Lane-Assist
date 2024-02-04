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
visibility: hidden
tags: 
  - documentation
---
!!!warning Warning
This page is meant for `developers`
!!!

## Data variable usage
The plugin will use the following data variable values:
=== [!badge variant="dark" text="Input"] ‎ data/path/to/some/input/var
Some kind of description.

=== [!badge variant="dark" text="Output"] ‎ data/path/to/some/output/var
Some kind of description.

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
**REMOVE / PLEASE FILL IN**