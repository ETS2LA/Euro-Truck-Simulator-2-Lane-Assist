from PIL import Image, ImageDraw, ImageFont
import dearpygui.dearpygui as dpg
import numpy as np
import threading
import time
import os

def get_font_only():
    font_path = 'Plugins/AR/Geist-Regular.ttf'
    return ImageFont.truetype(font_path, 64)

def create_text_renderer():
    os.makedirs("Plugins/AR/text_cache", exist_ok=True)
    
    font_path = 'Plugins/AR/Geist-Regular.ttf'
    fonts = {
        # Tried other sizes, just using the large one and
        # downscaling seems better
        #'small': ImageFont.truetype(font_path, 16),
        #'medium': ImageFont.truetype(font_path, 32),
        'large': ImageFont.truetype(font_path, 64)
    }
    
    texture_cache = {}
    with dpg.texture_registry() as texture_registry:
        pass
    
    return {
        'fonts': fonts,
        'cache': texture_cache,
        'registry_id': texture_registry
    }
    

class TextureText:
    def __init__(self, renderer):
        self.renderer = renderer
        self.fonts = renderer['fonts']
        self.cache = renderer['cache']
        self.registry_id = renderer['registry_id']
        
        threading.Thread(
            target=self.cache_clear_thread, 
            args=(20,), 
            daemon=True
        ).start()

    def get_text_texture(self, text):
        cache_key = f"{text}"
        
        if cache_key in self.cache:
            self.cache[cache_key]['time'] = time.time()
            return self.cache[cache_key]
        
        font = self.fonts['large']
        padding = 16
        
        # Calculate text dimensions
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        width = int((text_width + padding * 2))
        height = int((text_height + padding * 2))
        
        # Draw the text onto an image
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.text((1, 1), 
                  text, 
                  fill=(1,1,1,1),
                  font=font)
        
        # Convert the image to a numpy array for DPG
        data = np.array(image)
        texture_id = dpg.add_static_texture(width, height, data.flatten(), parent=self.registry_id)
        
        # Cache the texture info
        self.cache[cache_key] = {
            'id': texture_id,
            'width': width,
            'height': height,
            'time': time.time()
        }
        
        return self.cache[cache_key]
    
    def cache_clear_thread(self, max_age=10):
        while True:
            current_time = time.time()
            keys_to_delete = []
            
            for key, texture_info in self.cache.items():
                if current_time - texture_info['time'] > max_age:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                dpg.delete_item(self.cache[key]['id'])
                del self.cache[key]
    
            time.sleep(10)
    
    def draw_text(self, position, text, size=32, color=(255, 255, 255, 255), scale=1.0):
        if not text:
            return
            
        if len(color) == 4:
            r, g, b, a = color
        else:
            r, g, b = color
            a = 255

        # Get the texture
        texture_info = self.get_text_texture(text)
        scale = size / 64 * scale
        
        # Calculate position and draw
        x, y = position
        width = texture_info['width'] * scale
        height = texture_info['height'] * scale
        
        dpg.draw_image(
            texture_info['id'], 
            (x, y), 
            (x + width, y + height),
            uv_min=(0, 0),
            uv_max=(1, 1),
            color=(r, g, b, a)
        )