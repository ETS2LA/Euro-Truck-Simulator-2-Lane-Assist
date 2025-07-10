from ETS2LA.Utils.Values.text import ScrollingText
from Plugins.NGHUD.classes import HUDWidget
from PIL import Image, ImageDraw, ImageFont
import Plugins.AR.text as ARText
from Plugins.AR.classes import *
import threading
import datetime
import logging
import asyncio
import os

font = ARText.get_font_only()

if os.name == "nt":
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

class Widget(HUDWidget):
    name = "Media"
    description = "Displays media information such as song title, artist and playback progress."
    fps = 2
    
    title = ScrollingText("No Media Playing", max_width=20)
    artist = ScrollingText("No Artist", max_width=20)
    
    def __init__(self, plugin):
        super().__init__(plugin)
        threading.Thread(target=self.run_media_thread, daemon=True).start()
    
    def settings(self):
        return super().settings()
    
    async def media_info_thread(self):
        while True:
            try:
                media_manager = await MediaManager.request_async()
                current_session = media_manager.get_current_session()
                if current_session:
                    media_properties = await current_session.try_get_media_properties_async()
                    playback_info = current_session.get_timeline_properties()
                    if media_properties and playback_info:
                        self.media_info = {
                            "title": media_properties.title,
                            "artist": media_properties.artist.split("—")[0],
                            "start": playback_info.start_time,
                            "end": playback_info.end_time,
                            "position": playback_info.position
                        }
                else:
                    self.media_info = {}
            except Exception as e:
                logging.exception(f"Error fetching media info: {e}")
                self.media_info = {}
                
            await asyncio.sleep(5)

    def run_media_thread(self):
        """Run the media info thread in its own event loop"""
        asyncio.run(self.media_info_thread())
        
    def draw(self, offset_x, width, height=50):
        if not self.plugin.data:
            return
        
        title = self.media_info.get("title", "No Title")
        artist = self.media_info.get("artist", "No Artist")
        
        if title != self.title.text:
            self.title.text = title

        if artist != self.artist.text:
            self.artist.text = artist

        total_width = font.getbbox(title)[2] - font.getbbox(title)[0]
        per_character_width = total_width / len(title) if title else 1
        max_title_length = round((width - 10) / (per_character_width * (16/64)))
        max_artist_length = round((width - 10) / (per_character_width * (14/64)))
        
        self.title.max_width = max_title_length
        self.artist.max_width = max_artist_length
        
        # Start and end are datetime.timedelta    
        start = self.media_info.get("start", 0)
        end = self.media_info.get("end", 0)
        position = self.media_info.get("position", 0)
        
        if isinstance(start, (int, float)):
            start = datetime.timedelta(seconds=start)
        if isinstance(end, (int, float)):
            end = datetime.timedelta(seconds=end)

        duration = end.total_seconds() - start.total_seconds()
        progress = position.total_seconds() / duration if duration > 0 else 0

        self.data = [
            # Background
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            # Progress (same but lighter)
            Rectangle(
                Point(offset_x, 0, anchor=self.plugin.anchor),
                Point(width * progress + offset_x, height, anchor=self.plugin.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            Text(
                Point(10 + offset_x, 8, anchor=self.plugin.anchor),
                text=self.title.get(),
                color=Color(255, 255, 255, 200),
                size=16
            ),
            Text(
                Point(10 + offset_x, height-22, anchor=self.plugin.anchor),
                text=self.artist.get(),
                color=Color(255, 255, 255, 200),
                size=14
            )
        ]