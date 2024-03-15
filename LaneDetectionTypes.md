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
!!!success This is the reccomended lane detection type
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
!!!warning This is an outdated version of lane detection, not reccomended.
!!!

LSTR is an outdated version of lane detection. It scans the lane lines out of the windshield of your truck to know where they are.

Upsides:
- Honestly, there arent any.

Downsides:
- Does not work well during the night, or while raining
- Does not turn on sharp turns (it can't see them)
- Heavier on performance than Navigation Detection
- It requires a more difficult setup

=== UFLD (Ultra Fast Lane Detector) Lane Detection
!!!warning This is an outdated version of lane detection, not reccomended.
!!!
!!!danger This requires a GPU (NVIDIA GTX 1060 or better)
Using UFLD without a GPU is risky. It is very performance heavy and takes a ton of resources to run. Use it at your own risk.
!!!

UFLD is an outdated version of lane detection. It scans the lane lines out of the windshield of your truck to know where they are. This is more accurate than LSTR because it searches each pixel instead of groups.

Upsides:
- More accurate than LSTR

Downsides:
- Does not work well during the night, or while raining
- Does not turn on sharp turns (it can't see them)
- Very, very heavy on performance
- It requires a more difficult setup
===

## Future Plans
With the release of 2.0 currently scheduled for Q2-Q3 of 2024, there will be a new type of lane detection. This will use data directly from the game, meaning this will be the most accurate lane detection possible.

For people who are interested, this is the current state (as of 3-14-24). Prefabs and roads have been extracted, lane assist with this data is not currently possible.
[!embed](https://youtu.be/nOb0cKb9iC0)

Updates are regularly posted in the announcments channel of the [Discord](https://discord.com/channels/1120719484982939790/1120721331558817792). 
If you specifically only want development updates, head to the #roles channel and get the "Development News" role. You will get pinged in the annoncments channel whenever there is a update for 2.0.
