import os
import sys
from PIL import Image
from integrations.logger import log
from integrations.connection import check_connection, with_retry_on_connection_failure


# Import from pixoo directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pixoo.pixoo import Channel, Pixoo


# Helper class to manage interactions with the Divoom Pixoo device
class PixooDevice:
    def __init__(self, host: str, screen_size: int):
        self.host = host
        self.screen_size = screen_size
        self.pixoo = Pixoo(host, screen_size)

    # Attempt to verify connection to Pixoo device via API endpoint
    def check_connection(self):
        return check_connection(
            f'http://{self.host}/get',
            'Divoom Pixoo device',
            timeout=5,
            verify=True,
        )


    # Sets channel, visualizer or clock to the specified number
    # Available channels are: FACES (0) (The design selected via the Divoom app), CLOUD (1), VISUALIZER (2), and CUSTOM (3, 4, and 5)
    # The clock id is a number that corresponds to the installed clocks on your device
    # The visualizer id is a number that corresponds to the installed visualizers on your device
    @with_retry_on_connection_failure
    def generic_set_number(self, to_set, number):
        if to_set == 'channel':
            self.pixoo.set_channel(Channel(number))
        elif to_set == 'visualizer':
            self.pixoo.set_visualizer(number)
        elif to_set == 'clock':
            self.pixoo.set_clock(number)
        return 'OK'

    # Send the current buffer to the Pixoo display
    @with_retry_on_connection_failure
    def push(self):
        self.pixoo.push()

    # All "draw_" functions will draw to the screen buffer and not push the changes to the device unless the "push" parameter is set to True.

    # Draws a pixel at the specified coordinates in the requested color
    @with_retry_on_connection_failure
    def draw_pixel(self, x, y, r=255, g=255, b=255, push_now=False):
        self.pixoo.draw_pixel_at_location_rgb(int(x), int(y), int(r), int(g), int(b))
        if push_now: self.push()
        
        return 'OK'
    
    # Draws a single character at the specified coordinates in the requested color
    """
    Supported characters so far are:
    0123456789
    abcdefghijklmnopqrstuvwxyz
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    !'()+,-<=>?[]^_:;./{|}~$@%
    """
    @with_retry_on_connection_failure
    def draw_character(self, character, x=0, y=0, r=255, g=255, b=255, push_now=False):
        self.pixoo.draw_character_at_location_rgb(character, int(x), int(y), int(r), int(g), int(b))
        if push_now: self.push()
        
        return 'OK'

    # Draws a line from the specified start to end coordinates in the requested color
    @with_retry_on_connection_failure
    def draw_line(self, start_x, start_y, end_x, end_y, r=255, g=255, b=255, push_now=False):
        self.pixoo.draw_line_from_start_to_stop_rgb(int(start_x), int(start_y), int(end_x), int(end_y), int(r), int(g), int(b))
        if push_now: self.push()
        
        return 'OK'

    # Draws a border (non-filled rectangle) from the specified start to end coordinates in the requested color
    # Draws a outline around the screen by default
    @with_retry_on_connection_failure
    def draw_border(self, top_left_x=0, top_left_y=0, bottom_right_x=None, bottom_right_y=None, r=255, g=255, b=255, push_now=False):
        if bottom_right_x is None:
            bottom_right_x = self.screen_size - 1
        if bottom_right_y is None:
            bottom_right_y = self.screen_size - 1
        self.draw_line(top_left_x, top_left_y, bottom_right_x, top_left_y, r, g, b)  # Top
        self.draw_line(top_left_x, bottom_right_y, top_left_x, top_left_y, r, g, b)  # Left
        self.draw_line(bottom_right_x, bottom_right_y, top_left_x, bottom_right_y, r, g, b)  # Bottom
        self.draw_line(bottom_right_x, top_left_y, bottom_right_x, bottom_right_y, r, g, b, push_now)  # Right
        return 'OK'

    # Draws a filled rectangle from the specified start to end coordinates in the requested color
    @with_retry_on_connection_failure
    def draw_rectangle(self, top_left_x, top_left_y, bottom_right_x, bottom_right_y, r=255, g=255, b=255, push_now=False):
        self.pixoo.draw_filled_rectangle_from_top_left_to_bottom_right_rgb(
            int(top_left_x), int(top_left_y), int(bottom_right_x), int(bottom_right_y), int(r), int(g), int(b)
        )
        if push_now: self.push()
        
        return 'OK'

    # Fills screen with the specified color
    # Clears the screen by default
    @with_retry_on_connection_failure
    def draw_fill(self, r=0, g=0, b=0, push_now=False):
        self.pixoo.fill_rgb(int(r), int(g), int(b))
        if push_now: self.push()
        
        return 'OK'

    # Draws the specified text at the specified position in the specified color
    @with_retry_on_connection_failure
    def draw_text(self, text, x=0, y=0, r=255, g=255, b=255, push_now=False):
        self.pixoo.draw_text_at_location_rgb(text, int(x), int(y), int(r), int(g), int(b))
        if push_now: self.push()
        
        return 'OK'

    # Draws the specified image from the assets/images directory at the specified position
    @with_retry_on_connection_failure
    def draw_image(self, filename, x=0, y=0, rotate=0, resize=(None, None), push_now=False):
        # If it's a PIL image object, use it directly instead of loading from file
        if isinstance(filename, Image.Image):
            image = filename
            if rotate != 0:
                image = image.rotate(rotate, expand=True)
            if resize != (None, None):
                image = image.resize(resize, Image.BICUBIC)
            self.pixoo.draw_image_at_location(image, int(x), int(y))
        
        else:
            # Load the image from the assets/images directory
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'images', filename))
            image = Image.open(filename)

            # Convert PNG to RGBA
            if filename.endswith('.png'):
                image = image.convert('RGBA')
                background = Image.new('RGBA', image.size, (0, 0, 0))
                image = Image.alpha_composite(background, image)

            # Rotate the image if needed
            if rotate != 0:
                image = image.rotate(rotate, expand=True)

            # Resize the image if needed
            if resize != (None, None):
                image = image.resize(resize, Image.BICUBIC)

            self.pixoo.draw_image_at_location(image, int(x), int(y))

        if push_now: self.push()
        return 'OK'

    # Draws an arrow on the screen based on the specified direction, position, length, and color
    # Types: Flat, FortyFiveUp, FortyFiveDown, SingleUp, SingleDown, DoubleUp, DoubleDown
    @with_retry_on_connection_failure
    def draw_arrow(self, type, start_x, start_y, length=8, r=255, g=255, b=255, push_now=False):
        if length < 8 or length > self.screen_size:
            length = 8
            log('draw_arrow length too small. Setting to minimum length of 8.')

        if type == 'Flat':
            self.draw_image('right_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)
        elif type == 'FortyFiveUp':
            self.draw_image('upper_left_diagonal_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)
        elif type == 'FortyFiveDown':
            self.draw_image('upper_left_diagonal_arrow.png', start_x, start_y, rotate=270, resize=(length, length), push_now=push_now)
        elif type == 'SingleUp':
            self.draw_image('right_arrow.png', start_x, start_y, rotate=90, resize=(length, length), push_now=push_now)
        elif type == 'SingleDown':
            self.draw_image('right_arrow.png', start_x, start_y, rotate=270, resize=(length, length), push_now=push_now)
        elif type == 'DoubleUp':
            self.draw_image('up_double_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)
        elif type == 'DoubleDown':
            self.draw_image('up_double_arrow.png', start_x, start_y, rotate=180, resize=(length, length))
        else:
            self.draw_image('right_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)

    # Guide function: draws vertical and horizontal lines every 8 pixels
    @with_retry_on_connection_failure
    def draw_guide_lines(self, push_now=False):
        for i in range(0, self.screen_size, 8):
            # Draw vertical lines
            self.draw_line(i - 1, 0, i - 1, self.screen_size - 1, 128, 128, 128)
            self.draw_line(i, 0, i, self.screen_size - 1, 128, 128, 128)
            
            # Draw horizontal lines
            self.draw_line(0, i - 1, self.screen_size - 1, i - 1, 128, 128, 128)
            self.draw_line(0, i, self.screen_size - 1, i, 128, 128, 128)
            
        if push_now: self.push()
        
        return 'OK'

    # Guide function: draws pixels at the center and middle of each edge of the screen to help identify coordinates
    @with_retry_on_connection_failure
    def draw_guide_pixels(self, push_now=False):
        center = (self.screen_size - 1) // 2
        max_val = self.screen_size - 1

        # Top middle pixels
        self.draw_pixel(center, 0, 255, 0, 0)
        self.draw_pixel(center + 1, 0, 255, 0, 0)
        
        # Bottom middle pixels
        self.draw_pixel(center, max_val, 255, 0, 0)
        self.draw_pixel(center + 1, max_val, 255, 0, 0)
        
        # Left middle pixels
        self.draw_pixel(0, center, 255, 0, 0)
        self.draw_pixel(0, center + 1, 255, 0, 0)
        
        # Right middle pixels
        self.draw_pixel(max_val, center, 255, 0, 0)
        self.draw_pixel(max_val, center + 1, 255, 0, 0)
        
        # Center pixels
        self.draw_pixel(center, center, 255, 0, 0)
        self.draw_pixel(center + 1, center, 255, 0, 0)
        self.draw_pixel(center, center + 1, 255, 0, 0)
        self.draw_pixel(center + 1, center + 1, 255, 0, 0)

        if push_now: self.push()
        
        return 'OK'
