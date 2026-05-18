import os
import atexit
from time import sleep
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

from config import (
    CHANNEL_TIME,
    DEBUG,
    NIGHTSCOUT_URL,
    PIXOO_HOST,
    PIXOO_SCREEN_SIZE,
    SCREEN_CENTER,
    GLUCOSE_URGENT_LOW,
    GLUCOSE_LOW,
    GLUCOSE_NORMAL_MAX,
    GLUCOSE_HIGH,
    COLOR_URGENT_LOW,
    COLOR_LOW,
    COLOR_NORMAL,
    COLOR_HIGH,
    COLOR_URGENT_HIGH,
)
from pixoo_helper import PixooDevice
from nightscout import NightscoutClient


# Graceful shutdown handler to set Pixoo channel to "Cloud" when exiting
def _shutdown(pixoo_device):
    # pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Exiting. Setting channel to "Cloud".')



# Class to retrieve data from Nightscout and manage the display logic on the Pixoo device
class DisplayManager:
    def __init__(self, ns_client: NightscoutClient, pixoo_device: PixooDevice):
        self.ns_client = ns_client
        self.pixoo_device = pixoo_device

    # Parse the latest Nightscout response and return shared values
    def _get_latest_nightscout_info(self):
        current_sgv, current_direction, delta, time = self.ns_client.get_latest_sgv()
        
        # Calculate how long ago the data point was from the current time
        data_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        time_diff = now - data_time
        time_diff_minutes = int(time_diff.total_seconds() // 60)
        
        add_s = 's' if time_diff_minutes != 1 else ''
        
        return current_sgv, current_direction, delta, f"{time_diff_minutes} min{add_s} ago"

    # Choose the SGV color based on configured thresholds
    def _get_glucose_color(self, sgv_str: str):
        try:
            sgv = int(sgv_str)
        except (TypeError, ValueError):
            return COLOR_NORMAL

        if sgv < GLUCOSE_URGENT_LOW:
            return COLOR_URGENT_LOW
        if sgv < GLUCOSE_LOW:
            return COLOR_LOW
        if sgv <= GLUCOSE_NORMAL_MAX:
            return COLOR_NORMAL
        if sgv < GLUCOSE_HIGH:
            return COLOR_HIGH
        return COLOR_URGENT_HIGH

    # Load and scale an arrow image for the direction icon
    def _load_arrow_image(self, direction: str, size: int = 12) -> Image:
        direction_map = {
            'Flat': ('right_arrow.png', 0),
            'FortyFiveUp': ('upper_left_diagonal_arrow.png', 0),
            'FortyFiveDown': ('upper_left_diagonal_arrow.png', 270),
            'SingleUp': ('right_arrow.png', 90),
            'SingleDown': ('right_arrow.png', 270),
            'DoubleUp': ('up_double_arrow.png', 0),
            'DoubleDown': ('up_double_arrow.png', 180),
        }
        filename, rotation = direction_map.get(direction, ('right_arrow.png', 0))
        arrow_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', filename))

        try:
            arrow = Image.open(arrow_path).convert('RGBA')
            if rotation != 0:
                arrow = arrow.rotate(rotation, expand=False)
            return arrow.resize((size, size), Image.LANCZOS)
        except Exception as e:
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Error loading arrow image: {e}')
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Build the PIL image for the enhanced Nightscout display
    def _render_nightscout_image(self, sgv: str, delta: str, direction: str, time_ago: str) -> Image:
        img = Image.new('RGB', (PIXOO_SCREEN_SIZE, PIXOO_SCREEN_SIZE), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Load fonts
        font_large = ImageFont.truetype('assets/fonts/pixel_font-7.ttf', 36)
        font_medium = ImageFont.truetype('assets/fonts/thin_pixel-7.ttf', 20)
        font_small = ImageFont.truetype('assets/fonts/Micro5.ttf', 14)
        
        border_width = 2
        spacing = 4
        
        # Draw border around the entire screen in SGV color
        sgv_color = self._get_glucose_color(sgv)
        draw.rectangle([(0, 0), (PIXOO_SCREEN_SIZE - 1, PIXOO_SCREEN_SIZE - 1)], outline=sgv_color, width=border_width)

        # Draw direction arrow at top, before delta
        size = 12
        arrow_img = self._load_arrow_image(direction, size)
        img.paste(arrow_img, (SCREEN_CENTER - size, spacing), arrow_img)

        # Draw delta below SGV if it's not zero
        if delta != "0":           
            draw.text((SCREEN_CENTER + size // 2, spacing + border_width), str(delta), anchor='lt', font=font_medium, fill=(169, 169, 169))

        # Draw SGV in the center
        sgv_x = SCREEN_CENTER
        sgv_y = SCREEN_CENTER + spacing
        draw.text((sgv_x, sgv_y), str(sgv), fill=sgv_color, anchor='mm', font=font_large)

        # Draw time difference at the bottom
        draw.text((SCREEN_CENTER + 1, PIXOO_SCREEN_SIZE - spacing), time_ago, anchor='mb', font=font_small)

        return img

    # Draw the latest Nightscout data using Pixoo primitives
    def draw_nightscout_info(self):
        current_sgv, current_direction, delta, time_diff_str = self._get_latest_nightscout_info()
        
        if DEBUG:
            self.pixoo_device.debug_lines()

        self.pixoo_device.draw_border()  # Draw the outer frame
        self.draw_clock()
        
        font_width = 4      # Each character is 4 pixels wide
        font_height = 5     # Each character is 5 pixels tall
        elements_count = 3  # SGV, delta, direction
        gaps_count = elements_count - 1  # Number of gaps between elements
        spacing = 4 # Spacing between elements
        total_block_height = (elements_count * font_height) + (gaps_count * spacing)
        
        # Calculate the starting point for the top element
        start_y = (PIXOO_SCREEN_SIZE - total_block_height) // 2
        
        # Generate the 4 coordinates stepping by (font_height + spacing)
        y_coords = [start_y + (i * (font_height + spacing)) for i in range(elements_count)]
               
        # Draw SGV
        sgv_text_width = len(current_sgv) * font_width
        sgv_x = SCREEN_CENTER - (sgv_text_width // 2)
        glucose_color = self._get_glucose_color(current_sgv)
        self.pixoo_device.draw_text(current_sgv, sgv_x, y_coords[0], r = glucose_color[0], g = glucose_color[1], b = glucose_color[2])

        # Draw delta if it's not zero
        if delta != "0":
            x = SCREEN_CENTER - (len(delta) * font_width // 2)  # Center the delta text 
            self.pixoo_device.draw_text(delta, x, y_coords[1], r = glucose_color[0], g = glucose_color[1], b = glucose_color[2])
            
        # Draw the direction arrow
        self.pixoo_device.draw_arrow(current_direction, SCREEN_CENTER - 7 // 2, y_coords[2])
        
        # Draw border around the center block
        self.pixoo_device.draw_border(sgv_x -  spacing, y_coords[0] - spacing, sgv_x + sgv_text_width + spacing, y_coords[-1] + (font_height + spacing))

        # Draw the time difference at the bottom
        self.pixoo_device.draw_text(time_diff_str, SCREEN_CENTER - (len(time_diff_str) * font_width // 2), PIXOO_SCREEN_SIZE - (spacing + font_height))
        
        if DEBUG:
            self.pixoo_device.debug_pixels()

    # Draw the latest Nightscout data using PIL rendering
    def draw_nightscout_info_pil(self):
        current_sgv, current_direction, delta, time_diff_str = self._get_latest_nightscout_info()
        processed_img = self._render_nightscout_image(current_sgv, delta, current_direction, time_diff_str)
        self.pixoo_device.draw_image(processed_img, 0, 0)

    # Draw the current time
    def draw_clock(self):
        x = SCREEN_CENTER - (8 * 4 // 2)  # Center the clock text (4 pixels per character and max 8 characters for time)
        y = 6
        self.pixoo_device.draw_text(datetime.now().strftime('%I:%M %p'), x, y)

    # Main loop to continuously update the display
    def run(self):
        while True:
            self.pixoo_device.draw_fill()   # Clear the screen
            
            self.draw_nightscout_info()     # Draw using Pixoo primitives
            self.pixoo_device.push()
            sleep(float(CHANNEL_TIME))
            
            self.pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
            sleep(float(CHANNEL_TIME))
            
            self.draw_nightscout_info_pil() # Draw using PIL rendering for enhanced visuals
            self.pixoo_device.push()
            sleep(float(CHANNEL_TIME))
            
            self.pixoo_device.generic_set_number("channel", 0)  # Change to "Faces" channel
            sleep(float(CHANNEL_TIME))


# Main entry point of the application
def main():
    
    # Initialize clients and check connections
    ns_client = NightscoutClient(NIGHTSCOUT_URL)
    pixoo_device = PixooDevice(PIXOO_HOST, PIXOO_SCREEN_SIZE)
    atexit.register(_shutdown, pixoo_device)

    try:
        ns_client.check_connection()
        pixoo_device.check_connection()
    except Exception as e:
        print(f"Failed to connect: {e}")
        return # Exit if we can't connect to either service


    # Initialize the DisplayManager with the Nightscout client and Pixoo device
    display_manager = DisplayManager(ns_client, pixoo_device)
    print("Running...")
    display_manager.run()


if __name__ == "__main__":
    main()

