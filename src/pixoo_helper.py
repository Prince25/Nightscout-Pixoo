import os
import sys
import time
import requests
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv, find_dotenv


# Import from pixoo directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))
from pixoo.pixoo import Channel, Pixoo


# Load the environment variables
dotenv_file = find_dotenv()
if not dotenv_file:
    raise FileNotFoundError('No .env file found.')
load_dotenv(dotenv_file, override=True)

pixoo_host = os.environ.get('PIXOO_HOST')
pixoo_screen_size = int(os.environ.get('PIXOO_SCREEN_SIZE'))
retry_delay = os.environ.get('PIXOO_RETRY_DELAY')


# Connect to the Pixoo device
while True:
    try:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Trying to connect to "{pixoo_host}" ... ', end='')
        if requests.get(f'http://{pixoo_host}/get').status_code == 200:
            print('OK.')
            break
    except Exception as error:
        print('FAILED. Sleeping' + retry_delay + 'seconds.')
        print('ERROR:', error)
        time.sleep(int(retry_delay))


# Initialize the Pixoo object
pixoo = Pixoo(pixoo_host, pixoo_screen_size)


""" Pixoo Helper Functions
All "draw_" functions will draw to the screen buffer and not push the changes to the device unless the "push" parameter is set to True.

generic_set_number(to_set, number)
    Sets channel, visualizer or clock to the specified number
    Available channels are: FACES (0), CLOUD (1), VISUALIZER (2), and CUSTOM (3, 4, and 5)
push()
draw_pixel(x, y, r=255, g=255, b=255, push_now=False)
draw_character(character, x=0, y=0, r=255, g=255, b=255, push_now=False)
draw_line(start_x, start_y, end_x, end_y, r=255, g=255, b=255, push_now=False)
draw_border(top_left_x=0, top_left_y=0, bottom_right_x=pixoo_screen_size-1, bottom_right_y=pixoo_screen_size-1, r=255, g=255, b=255, push_now=False)
draw_rectangle(top_left_x, top_left_y, bottom_right_x, bottom_right_y, r=255, g=255, b=255, push_now=False)
draw_fill(r=0, g=0, b=0, push_now=False)
draw_text(text, x=0, y=0, r=255, g=255, b=255, push_now=False)
draw_image(filename, x=0, y=0, rotate=0, resize=(None, None), push_now=False)
draw_arrow(type, start_x, start_y, length=8, r=255, g=255, b=255, push_now=False):
    Types: Flat, FortyFiveUp, FortyFiveDown, SingleUp, SingleDown, DoubleUp, DoubleDown
"""


# Sets channel, visualizer or clock to the specified number
# Available channels are: FACES (0) (The design selected via the Divoom app), CLOUD (1), VISUALIZER (2), and CUSTOM (3, 4, and 5)
# The clock id is a number that corresponds to the installed clocks on your device
# The visualizer id is a number that corresponds to the installed visualizers on your device
def generic_set_number(to_set, number):
    if to_set == 'channel':
        pixoo.set_channel(Channel(number))
    elif to_set == 'visualizer':
        pixoo.set_visualizer(number)
    elif to_set == 'clock':
        pixoo.set_clock(number)
    return 'OK'


# Pushes the buffer to the device
def push(): pixoo.push()


# Draws a pixel at the specified coordinates in the requested color
def draw_pixel(x, y, r=255, g=255, b=255, push_now=False):
    pixoo.draw_pixel_at_location_rgb(
        int(x),
        int(y),
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Draws a single character at the specified coordinates in the requested color
"""
Supported characters so far are:
0123456789
abcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZ
!'()+,-<=>?[]^_:;./{|}~$@%
"""
def draw_character(character, x=0, y=0, r=255, g=255, b=255, push_now=False):
    pixoo.draw_character_at_location_rgb(
        character,
        int(x),
        int(y),
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Draws a line from the specified start to end coordinates in the requested color
def draw_line(start_x, start_y, end_x, end_y, r=255, g=255, b=255, push_now=False):
    pixoo.draw_line_from_start_to_stop_rgb(
        int(start_x),
        int(start_y),
        int(end_x),
        int(end_y),
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Draws a border (non-filled rectangle) from the specified start to end coordinates in the requested color
# Draws a outline around the screen by default
def draw_border(top_left_x=0, top_left_y=0, bottom_right_x=pixoo_screen_size-1, bottom_right_y=pixoo_screen_size-1, r=255, g=255, b=255, push_now=False):
    draw_line(top_left_x, top_left_y, bottom_right_x, top_left_y, r, g, b) # Top Horizontal
    draw_line(top_left_x, bottom_right_y, top_left_x, top_left_y, r, g, b) # Left Vertical
    draw_line(bottom_right_x, bottom_right_y, top_left_x, bottom_right_y, r, g, b) # Bottom Horizontal
    draw_line(bottom_right_x, top_left_y, bottom_right_x, bottom_right_y, r, g, b, push_now) # Right Vertical

    return 'OK'


# Draws a filled rectangle from the specified start to end coordinates in the requested color
def draw_rectangle(top_left_x, top_left_y, bottom_right_x, bottom_right_y, r=255, g=255, b=255, push_now=False):
    pixoo.draw_filled_rectangle_from_top_left_to_bottom_right_rgb(
        int(top_left_x),
        int(top_left_y),
        int(bottom_right_x),
        int(bottom_right_y),
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Fills screen with the specified color
# Clears the screen by default
def draw_fill(r=0, g=0, b=0, push_now=False):
    pixoo.fill_rgb(
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Draws the specified text at the specified position in the specified color
def draw_text(text, x=0, y=0, r=255, g=255, b=255, push_now=False):
    pixoo.draw_text_at_location_rgb(
        text,
        int(x),
        int(y),
        int(r),
        int(g),
        int(b)
    )

    if push_now: push()
    return 'OK'


# Draws the specified image at the specified position
def draw_image(filename, x=0, y=0, rotate=0, resize=(None, None), push_now=False):
    filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets', filename))
    image = Image.open(filename)

    # Convert PNG to RGBA
    if filename.endswith('.png'):
        image = Image.open(filename).convert('RGBA')
        background = Image.new('RGBA', image.size, (0, 0, 0))
        image = Image.alpha_composite(background, image)
        
    # Rotate the image if needed
    if rotate != 0:
        image = image.rotate(rotate, expand=True)
    
    # Resize the image if needed
    if resize != (None, None):
        image = image.resize(resize, Image.BICUBIC)

    pixoo.draw_image_at_location(
        image,
        int(x),
        int(y)
    )

    if push_now: push()
    return 'OK'


# Draws an arrow on the screen based on the specified direction, position, length, and color
# Types: Flat, FortyFiveUp, FortyFiveDown, SingleUp, SingleDown, DoubleUp, DoubleDown
def draw_arrow(type, start_x, start_y, length=8, r=255, g=255, b=255, push_now=False):
    if length < 8 or length > pixoo_screen_size: 
        length = 8  # Minimum length is between 8 and the screen size
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow length too small. Setting to minimum length of 8.')

    # Draw the arrow
    if type == 'Flat':
        draw_image('right_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)

    elif type == 'FortyFiveUp':
        draw_image('upper_left_diagonal_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)

    elif type == 'FortyFiveDown':
        draw_image('upper_left_diagonal_arrow.png', start_x, start_y, rotate=270, resize=(length, length), push_now=push_now)

    elif type == 'SingleUp':
        draw_image('right_arrow.png', start_x, start_y, rotate=90, resize=(length, length), push_now=push_now)

    elif type == 'SingleDown':
        draw_image('right_arrow.png', start_x, start_y, rotate=270, resize=(length, length), push_now=push_now)

    elif type == 'DoubleUp':
        draw_image('up_double_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)

    elif type == 'DoubleDown':
        draw_image('up_double_arrow.png', start_x, start_y, rotate=180, resize=(length, length))

    else:
        draw_image('right_arrow.png', start_x, start_y, rotate=0, resize=(length, length), push_now=push_now)


# Debug function: draws vertical and horizontal lines every 8 pixels
def debug_lines(push_now=False):
    for i in range(0, pixoo_screen_size, 8):      
        # Draw vertical lines
        draw_line(i-1, 0, i-1, pixoo_screen_size - 1, 128, 128, 128)
        draw_line(i, 0, i, pixoo_screen_size - 1, 128, 128, 128)
        # Draw horizontal lines
        draw_line(0, i-1, pixoo_screen_size - 1, i-1, 128, 128, 128)
        draw_line(0, i, pixoo_screen_size - 1, i, 128, 128, 128)
    
    if push_now: push()
    return 'OK'


# Debug function: draws pixels at the center and middle of each edge of the screen to help identify coordinates
def debug_pixels(push_now=False):
    center = (pixoo_screen_size - 1) // 2
    max = pixoo_screen_size - 1
    
    # Top middle pixels
    draw_pixel(center, 0, 255, 0, 0)
    draw_pixel(center + 1, 0, 255, 0, 0)
    
    # Bottom middle pixels
    draw_pixel(center, max, 255, 0, 0)
    draw_pixel(center + 1, max, 255, 0, 0)
    
    # Left middle pixels
    draw_pixel(0, center, 255, 0, 0)
    draw_pixel(0, center + 1, 255, 0, 0)
    
    # Right middle pixels
    draw_pixel(max, center, 255, 0, 0)
    draw_pixel(max, center + 1, 255, 0, 0)
    
    # Center pixels
    draw_pixel(center, center, 255, 0, 0)
    draw_pixel(center + 1, center, 255, 0, 0)
    draw_pixel(center, center + 1, 255, 0, 0)
    draw_pixel(center + 1, center + 1, 255, 0, 0)
    
    if push_now: push()
    return 'OK'
