"""This plugin handles turning the offset values into a steering angle for the game.

Uses the following variables from data:
```
input: data["LaneDetection"]["difference"]
output: data["controller"]["leftStick"]
```"""