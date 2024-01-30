---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-30
icon: comment-discussion
---

!!!warning Warning
This page is meant for `developers`
!!!

## Directly usable functions and values
```python
from src.translator import Translate
from src.logger import print

print(Translate("Hello world!"))
```

## Description
Provides a standard translation interface. All settings are handled on the interface side, so everything wrapped in the `Translate()` function automatically get's the correct language.

**All functions in `src.helpers` already use this interface by default.**