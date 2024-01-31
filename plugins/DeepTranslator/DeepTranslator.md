---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-1-31
icon: stack
tags:
  - panel
---


### Description
This panel will provide an interface with the translation backend. For the user this basically means selecting the language you want to translate the app to.

!!!warning Warning
**The translations may be incorrect, they might break the UI, and they might make the app unusable.**
There are too many languages in the world for us to translate to manually, and the UI elements will not automatically scale. Thus if your language has longer words than english, many of the UI elements will break.
!!!

### Configuration / UI
All that is necessary for the average user is the language picker up top. Just select your language from the list, and the app will automatically translate to it using google translate.

### Installation
This panel will installer the following python packages:
```
deep_translator
```
!!! Note
Deep translator should already have been installed from the main `requirements.txt` file, since src.translator uses it too.
!!!

 