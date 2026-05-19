from datetime import datetime
from integrations.pixoo import PixooDevice
from config import (
    PIXOO_SCREEN_SIZE,
    SCREEN_CENTER,
)

DRAW_GUIDES = False  # Set to True to draw guides for debugging layout

# Renderer class using the Pixoo primitive library
class PixooRenderer:
    def __init__(self, device: PixooDevice):
        self.device = device
        self.font_width = 4      # Each character is 4 pixels wide
        self.font_height = 5     # Each character is 5 pixels tall
        self.elements_count = 3  # SGV, delta, direction
        self.gaps_count = self.elements_count - 1  # Number of gaps between elements
        self.spacing = 4  # Spacing between elements
        self.total_block_height = (self.elements_count * self.font_height) + (self.gaps_count * self.spacing)
    
    def _draw_clock(self):
        current_time = datetime.now().strftime('%I:%M %p')
        self.device.draw_text(
            current_time,
            x=SCREEN_CENTER - (len(current_time) * self.font_width // 2),  # Center the clock text
            y=self.font_height
        )

    def _draw_outer_border(self, glucose_color):
        self.device.draw_border(r=glucose_color[0], g=glucose_color[1], b=glucose_color[2])    

    def _draw_sgv(self, sgv, glucose_color, y):
        sgv_text = str(sgv)
        sgv_text_width = len(sgv_text) * self.font_width
        sgv_x = SCREEN_CENTER - (sgv_text_width // 2)
        self.device.draw_text(
            sgv_text,
            sgv_x,
            y,
            r=glucose_color[0],
            g=glucose_color[1],
            b=glucose_color[2],
        )
        return sgv_x, sgv_text_width

    def _draw_delta(self, delta, y):
        delta_text = str(delta)
        self.device.draw_text(
            delta_text,
            SCREEN_CENTER - (len(delta_text) * self.font_width // 2),
            y
        )

    def _draw_direction(self, direction, y):
        self.device.draw_arrow(direction, SCREEN_CENTER - 7 // 2, y)

    def _draw_center_block_border(self, sgv_x, sgv_text_width, y_coords):
        self.device.draw_border(
            sgv_x - self.spacing,
            y_coords[0] - self.spacing,
            sgv_x + sgv_text_width + self.spacing,
            y_coords[-1] + (self.font_height + self.spacing),
        )

    def _draw_time_ago(self, time_ago):
        self.device.draw_text(
            time_ago,
            SCREEN_CENTER - (len(time_ago) * self.font_width // 2),
            PIXOO_SCREEN_SIZE - (self.spacing + self.font_height),
        )
    
    def render(self, sgv, delta, direction, time_ago, glucose_color_func):
        if DRAW_GUIDES:
            self.device.draw_guide_lines()

        # Generate the 4 y coordinates stepping by (font_height + spacing)
        start_y = (PIXOO_SCREEN_SIZE - self.total_block_height) // 2
        y_coords = [start_y + (i * (self.font_height + self.spacing)) for i in range(self.elements_count)]
        
        # Draw elements in the order of clock, outer border, SGV, delta, direction, center block border, time ago
        glucose_color = glucose_color_func(sgv)
        self._draw_clock()
        self._draw_outer_border(glucose_color)
        sgv_x, sgv_text_width = self._draw_sgv(sgv, glucose_color, y_coords[0])

        if delta != "0":
            self._draw_delta(delta, y_coords[1])

        self._draw_direction(direction, y_coords[2])
        self._draw_center_block_border(sgv_x, sgv_text_width, y_coords)
        self._draw_time_ago(time_ago)

        if DRAW_GUIDES:
            self.device.draw_guide_pixels()
