---
authors: 
  - name: DylDev
    link: https://github.com/DylDevs
    avatar: https://avatars.githubusercontent.com/u/110776467?v=4
date: 2024-3-11
icon: checklist
tags: 
  - tutorial
---
# Lane Detection Types

!!! What is lane detection
Lane Detection is the way that ETS2 Lane Assist knows how to keep the truck inside of the lane. Currently, we use vision to do this. Wether that be searching for lanes on your screen, or looking at the minimap.

Navigation Detection is the best and is the default lane detection type.
!!!

<hr></hr>

=== Navigation Detection
!!! This is the reccomended lane detection type
!!!

Navigation Detection looks at the ingame minimap at the bottom right of your screen. In this minimap, there are lane lines that navigation Detection reads. This makes it the most accurate as it is getting lane data directly from the game.

Upsides:
- Accurate
- Low performance
- Easy to use

Downsides:
- Whenever you get a notification in the route advisor, Navigation Detection won't work. This is due to the minimap being blocked. We are looking into solutions for this.
- Icons and company names may mess lane detection up since Navigation Detection uses colors to search for lane lines. This can be fixed easily by installing the CleanRouteAdvisor mod.
=== LSTR Lane Detection

=== UFLD (Ultra Fast Lane Detector) Lane Detection

===

## Future Plans
With the release of 2.0 currently scheduled for Q2-Q3 of 2024, there will be a new type of lane detection. This will use data directly from the game, meaning this will be the most accurate lane detection possible.

[!embed](https://cdn.discordapp.com/attachments/1120721331558817792/1214653843938480169/2024-03-05_21-13-07_Trim.mp4?ex=6603200b&is=65f0ab0b&hm=52485f8cfd156ed450d9b23c0d7d9c2395fbecb60486b32437cb329204f0476a&)