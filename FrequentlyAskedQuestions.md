---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
date: 2024-3-14
icon: tasklist
tags: 
  - faq
---

!!!danger This page is incomplete
There are still a ton more topics to cover on this page, they will be added slowly. For now, you can contact support if you need any help with topics that aren't on the list.
!!!

# Question and Answer
!!! Quick Tip
Use the sidebar on the right to find the topic you are looking for instead of scrolling.
!!!

## Steering Doesn't Work
This can be multiple things.
#### 1. Check that the SDK Controller plugin is enabled.
  1.1. In the app, click the "Plugins" button on the leftmost sidebar
  1.2. Make sure that the SDKController plugin looks like this:
  ![Enabled SDK Controller Plugin](/assets/WikiFAQ/SDKController.png)
  If it is grey, you should double click it to enable it.
#### 2. Check that the input files exist
  !!! Note
  If you already know where ETS2 is located on your drive, go ahead and skip to 2.4
  !!!
  2.1. Open up Steam and head over to your libray
  2.2. Find ETS2 in your library, then hit this button:
  ![Settings button highlighted in red](/assets/WikiFAQ/Steam/ETS2InLibrary.png)
  2.3. Then, hit "Manage", and "Browse Local Files"
  ![Buttons highlighted in red](/assets/WikiFAQ/Steam/Options.png)
  2.4. In the file explorer window that opens, go through these folders:
  ```bin > win_x64 > plugins```
  2.5. In this directory, there should be 2 files:
    input_semantical.dll
    scs_telemetry.dll
  If these files are not there, or the plugins folder does not exist, you should run First Time Setup again.

#### 3. Contact Us
  [!ref Contact Us](/FAQ/ContactUs.md)