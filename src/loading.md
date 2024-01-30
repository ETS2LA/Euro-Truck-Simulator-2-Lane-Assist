---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: hourglass
---

!!!warning Warning
This page is meant for `developers`
!!!

## Directly usable functions and values
```python
from src.loading import LoadingWindow

# Make a new loading window
loading = LoadingWindow("Running heavy task...")

while not heavyTaskDone:
    # Do heavy task
    loading.update(progress=heavyTaskProgress, text=f"Running heavy task... {round(heavyTaskProgress,1)}%")
# When done
loading.destroy()
```

## Description
Provides an easy to use loading window for heavy tasks. It's quite simple to use just by looking at the example code above.