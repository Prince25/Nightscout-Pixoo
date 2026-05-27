import os
from integrations.logger import log
from PIL import Image, ImageDraw, ImageFont
from config import (
    PIXOO_SCREEN_SIZE,
    SCREEN_CENTER,
)


class PilRenderer:
    def __init__(self):
        pass

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
        arrow_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'images', filename))

        try:
            arrow = Image.open(arrow_path).convert('RGBA')
            if rotation != 0:
                arrow = arrow.rotate(rotation, expand=False)
            return arrow.resize((size, size), Image.LANCZOS)
        except Exception as e:
            log(f'Error loading arrow image: {e}')
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Build the PIL image for the enhanced Nightscout display
    def _render_nightscout_image(self, sgv: str, delta: str, direction: str, time_ago: str, glucose_color_func):
        img = Image.new('RGB', (PIXOO_SCREEN_SIZE, PIXOO_SCREEN_SIZE), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Load fonts
        font_large = ImageFont.truetype('assets/fonts/pixel_font-7.ttf', 32)
        font_medium = ImageFont.truetype('assets/fonts/thin_pixel-7.ttf', 20)
        font_small = ImageFont.truetype('assets/fonts/Micro5.ttf', 14)

        border_width = 2
        spacing = 4

        # Draw border around the entire screen in SGV color
        sgv_color = glucose_color_func(sgv)
        draw.rectangle(
            [(0, 0), (PIXOO_SCREEN_SIZE - 1, PIXOO_SCREEN_SIZE - 1)],
            outline=sgv_color,
            width=border_width,
        )

        # Draw direction arrow at top, before delta
        size = 12
        arrow_img = self._load_arrow_image(direction, size)
        img.paste(arrow_img, (SCREEN_CENTER - size, spacing), arrow_img)

        # Draw delta below SGV if it's not zero
        if delta != "0":
            draw.text(
                (SCREEN_CENTER + size // 2, spacing + border_width),
                str(delta),
                anchor='lt',
                font=font_medium,
                fill=(169, 169, 169),
            )

        # Draw SGV in the center
        sgv_x = SCREEN_CENTER
        sgv_y = SCREEN_CENTER + spacing
        draw.text((sgv_x, sgv_y), str(sgv), fill=sgv_color, anchor='mm', font=font_large)

        # Draw time difference at the bottom
        draw.text((SCREEN_CENTER + 1, PIXOO_SCREEN_SIZE - spacing), time_ago, anchor='mb', font=font_small)

        return img

    def render(self, sgv, delta, direction, time_ago, glucose_color_func):
        return self._render_nightscout_image(sgv, delta, direction, time_ago, glucose_color_func)
