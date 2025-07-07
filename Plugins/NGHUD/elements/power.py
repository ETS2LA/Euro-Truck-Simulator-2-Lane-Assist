from Plugins.NGHUD.classes import HUDWidget
from Plugins.AR.classes import *
import logging
import os

class Widget(HUDWidget):
    name = "Throttle / Brake"
    description = "Display current throttle and brake percentage."
    fps = 10
    
    def __init__(self, plugin):
        super().__init__(plugin)
    
    def settings(self):
        return super().settings()
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        gameThrottle = self.plugin.data["truckFloat"]["userThrottle"]
        gameBrake = self.plugin.data["truckFloat"]["userBrake"]
        
        data = []
        
        display_value = 0
        if gameThrottle > 0.01:
            display_value = gameThrottle
            data.append(
                # Progress for Throttle (left to right)
                Rectangle(
                    Point(offset_x, 0, anchor=self.plugin.anchor),
                    Point(width * gameThrottle + offset_x, height, anchor=self.plugin.anchor),
                    color=Color(150, 255, 150, 20),
                    fill=Color(150, 255, 150, 10),
                    rounding=6,
                ),
            )
        elif gameBrake > 0.01:
            display_value = -gameBrake
            data.append(
                # Progress for Brake (right to left)
                Rectangle(
                    Point(width * (1 - gameBrake) + offset_x, 0, anchor=self.plugin.anchor),
                    Point(width + offset_x, height, anchor=self.plugin.anchor),
                    color=Color(255, 150, 150, 20),
                    fill=Color(255, 150, 150, 10),
                    rounding=6,
                ),
            )
            

        data += [
            # Background
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(10 + offset_x, 8, anchor=self.plugin.anchor),
                text=f"{display_value*100:.0f}",
                color=Color(255, 255, 255, 200),
                size=32
            ),
            Text(
                Point(width-20 + offset_x, height-20, anchor=self.plugin.anchor),
                text=f"%",
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]
        
        self.data = data