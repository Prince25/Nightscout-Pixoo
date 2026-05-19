from time import sleep
from datetime import datetime, timezone
from config import (
    CHANNEL_TIME,
    DEBUG,
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
from integrations.pixoo import PixooDevice
from integrations.nightscout import NightscoutClient
from .renderers.pixoo_renderer import PixooRenderer
from .renderers.pil_renderer import PilRenderer


# Class to retrieve data from Nightscout and manage the display logic on the Pixoo device
class DisplayManager:
    def __init__(self, ns_client: NightscoutClient, pixoo_device: PixooDevice, pixoo_renderer=None, pil_renderer=None):
        self.ns_client = ns_client
        self.pixoo_device = pixoo_device
        self.pixoo_renderer = pixoo_renderer or PixooRenderer(self.pixoo_device)
        self.pil_renderer = pil_renderer or PilRenderer()

    # Parse the latest Nightscout response and return shared values
    def _get_latest_nightscout_info(self):
        current_sgv, current_direction, delta, time = self.ns_client.get_latest_sgv()

        # Calculate how long ago the data point was from the current time
        data_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        time_diff = now - data_time
        time_diff_minutes = int(time_diff.total_seconds() // 60)
        add_s = 's' if time_diff_minutes != 1 else '' # Add 's' for plural minutes

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

    # Draw the latest Nightscout data using Pixoo primitives
    def draw_nightscout_info(self):
        current_sgv, current_direction, delta, time_diff_str = self._get_latest_nightscout_info()
        self.pixoo_renderer.render(current_sgv, delta, current_direction, time_diff_str, self._get_glucose_color)

    # Draw the latest Nightscout data using PIL rendering
    def draw_nightscout_info_pil(self):
        current_sgv, current_direction, delta, time_diff_str = self._get_latest_nightscout_info()
        processed_img = self.pil_renderer.render(current_sgv, delta, current_direction, time_diff_str, self._get_glucose_color)
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

            self.pixoo_device.generic_set_number('channel', 1)  # Change to "Cloud" channel
            sleep(float(CHANNEL_TIME))

            self.draw_nightscout_info_pil() # Draw using PIL rendering for enhanced visuals
            self.pixoo_device.push()
            sleep(float(CHANNEL_TIME))

            self.pixoo_device.generic_set_number('channel', 0)  # Change to "Faces" channel
            sleep(float(CHANNEL_TIME))
