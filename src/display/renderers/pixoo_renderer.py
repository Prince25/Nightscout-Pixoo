from datetime import datetime
from integrations.pixoo import PixooDevice
from config import (
    DEBUG,
    PIXOO_SCREEN_SIZE,
    SCREEN_CENTER,
)

# Renderer class using the Pixoo primitive library
class PixooRenderer:
    def __init__(self, device: PixooDevice):
        self.device = device

    def render(self, sgv, delta, direction, time_ago, glucose_color_func):
        if DEBUG:
            self.device.debug_lines()

        self.device.draw_border()  # Draw the outer frame
        self.device.draw_text(
            datetime.now().strftime('%I:%M %p'),
            SCREEN_CENTER - (8 * 4 // 2),
            6,
        )

        font_width = 4      # Each character is 4 pixels wide
        font_height = 5     # Each character is 5 pixels tall
        elements_count = 3  # SGV, delta, direction
        gaps_count = elements_count - 1  # Number of gaps between elements
        spacing = 4  # Spacing between elements
        total_block_height = (elements_count * font_height) + (gaps_count * spacing)

        # Calculate the starting point for the top element
        start_y = (PIXOO_SCREEN_SIZE - total_block_height) // 2
        
        # Generate the 4 coordinates stepping by (font_height + spacing)
        y_coords = [start_y + (i * (font_height + spacing)) for i in range(elements_count)]

        # Draw SGV
        sgv_text_width = len(str(sgv)) * font_width
        sgv_x = SCREEN_CENTER - (sgv_text_width // 2)
        glucose_color = glucose_color_func(sgv)
        self.device.draw_text(
            str(sgv),
            sgv_x,
            y_coords[0],
            r=glucose_color[0],
            g=glucose_color[1],
            b=glucose_color[2],
        )
        
        # Draw delta if it's not zero
        if delta != "0":
            x = SCREEN_CENTER - (len(str(delta)) * font_width // 2)
            self.device.draw_text(
                str(delta),
                x,
                y_coords[1],
                r=glucose_color[0],
                g=glucose_color[1],
                b=glucose_color[2],
            )

        # Draw the direction arrow
        self.device.draw_arrow(direction, SCREEN_CENTER - 7 // 2, y_coords[2])

        # Draw border around the center block
        self.device.draw_border(
            sgv_x - spacing,
            y_coords[0] - spacing,
            sgv_x + sgv_text_width + spacing,
            y_coords[-1] + (font_height + spacing),
        )

        # Draw the time difference at the bottom
        self.device.draw_text(
            time_ago,
            SCREEN_CENTER - (len(time_ago) * font_width // 2),
            PIXOO_SCREEN_SIZE - (spacing + font_height),
        )

        if DEBUG:
            self.device.debug_pixels()
