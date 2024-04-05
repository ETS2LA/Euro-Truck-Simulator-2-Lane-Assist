---
authors: 
  - name: Tumppi066
    link: https://github.com/Tumppi066
    avatar: https://avatars.githubusercontent.com/u/83072683?v=4
date: 2024-04-05
icon: typography
---
!!! Note
Translation was an afterthought for ETS2LA V1. 
Translating works perfectly, but it's a bit more manual than is ideal.
!!!
# Translating
This page will help you translate ETS2LA to the language of your choice.

### How to create the translation file correctly.
Due to the way the application was developed, V1 does not have a native translation file. This means that you will have to open each panel after selecting the language, and translate the text manually.
1. Open the app and select the language you want to translate to.
2. Manually **open each of the pages you want to translate**. Note that this also means all popups (like the close app confirmation).
3. Go into the translation settings page and click on the *Create Manual Cache* button. (make sure you have the language selected still)
   
### How to translate the text.
The file should look something like this:
```json
{
    "Panels": "Paneelit",
    "Plugins": "Plugins",
    "Performance": "Esitys",
    "Settings": "asetukset",
    "Controls": "Säätimet",
    "Help/About": "Ohje/Tietoja",
    "Feedback": "Palaute"
}
```
It's automatically populated with the Google Translate based translations, and all you have to do is replace the right side of the colon with the correct translation. In case a manual translation file exists, the app will prioritize this instead of the Google Translate cache.
!!! Note
The file might contain encoding issues (for example, **ä = \u00e4**), you can still replace them with the correct character. The app is also able to read the escaped characters.
!!!