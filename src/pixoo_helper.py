import os
import sys
import time
import json
import base64
import requests
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv, find_dotenv


# Import from pixoo directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))
from pixoo.pixoo import Channel, Pixoo


# Load the environment variables
load_dotenv(find_dotenv())
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

brightness(percentage)
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
draw_image(path, x=0, y=0, push_now=False)
draw_arrow(direction, start_x, start_y, length=7, r=255, g=255, b=255, tip_length_ratio=3, push_now=False):
    Types: Flat, FortyFiveUp, FortyFiveDown, SingleUp, SingleDown, DoubleUp, DoubleDown
send_gif(path, speed=100)
    Higher speed = slower
send_text(text, xy=(0, 0), color=(255, 255, 255), identifier=1, font=2, width=64)
    Currently Unreliable
"""

# Sets the brightness to the specified number
def brightness(percentage):
    pixoo.set_brightness(percentage)
    return 'OK'


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
def draw_image(path, x=0, y=0, push_now=False):
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'media', path))
    image = Image.open(path)

    # Convert PNG to RGBA if necessary
    if path.endswith('.png'):
        image = Image.open(path).convert('RGBA')
        background = Image.new('RGBA', image.size, (0, 0, 0))
        image = Image.alpha_composite(background, image)

    pixoo.draw_image_at_location(
        image,
        int(x),
        int(y)
    )

    if push_now: push()
    return 'OK'


# Draws an arrow on the screen based on the specified direction, position, length, and color
# Types: Flat, FortyFiveUp, FortyFiveDown, SingleUp, SingleDown, DoubleUp, DoubleDown
def draw_arrow(type, start_x, start_y, length=7, r=255, g=255, b=255, push_now=False):
    if length <= 2: 
        length = 3  # Minimum length is 3
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow length too small. Setting to minimum length of 3.')

    tip_length = int(length * (2/3) + 1)

    # Make sure the arrow doesn't go off the screen
    # TODO: Make this more robust or delete?
    if start_x < 0 or start_x >= pixoo_screen_size:
        start_x = 0
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow x coordinate out of screen. Range: 0 - {pixoo_screen_size - 1}. Setting to 0.')
    if start_y < 0 or start_y >= pixoo_screen_size:
        start_y = 0
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow y coordinate out of screen. Range: 0 - {pixoo_screen_size - 1}. Setting to 0.')

    # if start_x - length < 0 or start_y - length < 0: # Up facing arrows
    #     start_y = length
    #     length = 7
    #     print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow up length out of screen. Range: 0 - {pixoo_screen_size - 1}. Setting to defaults.')
    # elif start_x + length > pixoo_screen_size or start_y + length > pixoo_screen_size: # Down facing arrows
    #     start_x = start_y = 0
    #     length = 7
    #     print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | draw_arrow down length out of screen. Range: 0 - {pixoo_screen_size - 1}. Setting to defaults.')

    # Draw the arrow
    if type == 'Flat':
        end_x = start_x + length
        end_y = start_y
        tip_length //= 1.5 # Make the tip a bit shorter
        draw_line(start_x, start_y, end_x, end_y, r, g, b) # Horizontal line
        draw_line(end_x, end_y, end_x - tip_length, end_y - tip_length, r, g, b) # Diagonal Up line
        draw_line(end_x, end_y, end_x - tip_length, end_y + tip_length, r, g, b, push_now) # Diagonal Down line

    elif type == 'FortyFiveUp':
        end_x = start_x + length
        end_y = start_y - length
        draw_line(start_x, start_y, end_x, end_y, r, g, b) # Diagonal line
        draw_line(end_x, end_y, end_x, end_y + tip_length, r, g, b) # Vertical line
        draw_line(end_x, end_y, end_x - tip_length, end_y, r, g, b, push_now) # Horizontal line

    elif type == 'FortyFiveDown':
        end_x = start_x + length
        end_y = start_y + length
        draw_line(start_x, start_y, end_x, end_y, r, g, b) # Diagonal line
        draw_line(end_x, end_y, end_x, end_y - tip_length, r, g, b) # Vertical line
        draw_line(end_x, end_y, end_x - tip_length, end_y, r, g, b, push_now) # Horizontal line

    elif type == 'SingleUp':
        end_x = start_x
        end_y = start_y - length
        tip_length //= 1.5 # Make the tip a bit shorter
        draw_line(start_x, start_y, end_x, end_y, r, g, b) # Vertical line
        draw_line(end_x, end_y, end_x - tip_length, end_y + tip_length, r, g, b) # Diagonal Left line
        draw_line(end_x, end_y, end_x + tip_length, end_y + tip_length, r, g, b, push_now) # Diagonal Right line

    elif type == 'SingleDown':
        end_x = start_x
        end_y = start_y + length
        tip_length //= 1.5 # Make the tip a bit shorter
        draw_line(start_x, start_y, end_x, end_y, r, g, b) # Vertical line
        draw_line(end_x, end_y, end_x - tip_length, end_y - tip_length, r, g, b) # Diagonal Left line
        draw_line(end_x, end_y, end_x + tip_length, end_y - tip_length, r, g, b, push_now) # Diagonal Right line

    elif type == 'DoubleUp':
        draw_arrow('SingleUp', start_x, start_y, length, r, g, b)
        draw_arrow('SingleUp', start_x + tip_length + 1, start_y, length, r, g, b, push_now)

    elif type == 'DoubleDown':
        draw_arrow('SingleDown', start_x, start_y, length, r, g, b)
        draw_arrow('SingleDown', start_x + tip_length + 1, start_y, length, r, g, b, push_now)

    else:
        draw_text('???', start_x, start_y, r, g, b, push_now)


def _reset_gif():
    return requests.post(f'http://{pixoo.address}/post', json.dumps({
        "Command": "Draw/ResetHttpGifId"
    })).json()

def _send_gif(num, offset, width, speed, data):
    return requests.post(f'http://{pixoo.address}/post', json.dumps({
        "Command": "Draw/SendHttpGif",
        "PicID": 1,
        "PicNum": num,
        "PicOffset": offset,
        "PicWidth": width,
        "PicSpeed": speed,
        "PicData": data
    })).json()

# Draws a gif. Higher speed = slower.
def send_gif(path, speed=100):
    gif = Image.open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'media', path)))
    speed = int(speed)

    if gif.is_animated:
        _reset_gif()

        for i in range(gif.n_frames):
            gif.seek(i)

            if gif.size not in ((16, 16), (32, 32), (64, 64)):
                gif_frame = gif.resize((pixoo.size, pixoo.size)).convert("RGB")
            else:
                gif_frame = gif.convert("RGB")

            _send_gif(
                gif.n_frames,
                i,
                gif_frame.width,
                speed,
                base64.b64encode(gif_frame.tobytes()).decode("utf-8")
            )
    else:
        pixoo.draw_image(gif)
        push()

    return 'OK'


'''
NOTE: Currently Unreliable
Send text to the display using (currently seemingly in alpha) text functionality
def send_text(self, text, xy=(0, 0), color=(255, 255, 255), identifier=1, font=2, width=64,
              movement_speed=0,
              direction=TextScrollDirection.RIGHT):
The first argument is the string to be displayed (required)
The second argument is the position to place the string (optional, default (0, 0))
the third argument is the color of the text (optional, default (255, 255, 255))
The fourth is the text identifier. Use this to update existing text on the display (optional, default 1, has to be
between 0 and 20)
The fifth is the font identifier (optional, default 2, has to be between 0 and 7 but support seems limited for some fonts)
The sixth argument is the width of the "textbox" (optional, default 64)
The seventh argument is the movement speed of the text in case it doesn't fit the "textbox" (optional, default 0)
    **NOTE:** Currently there seems to be no way to stop the movement
The eight and final argument is the movement direction of the text (optional, default TextScrollDirection.LEFT)
    **NOTE:** Currently TextScrollDirection.RIGHT seems broken on the display
NOTE: Currently this is **not** a drawing method, so it'll add the text over whatever is already on screen
'''
def send_text(text, xy=(0, 0), color=(255, 255, 255), identifier=1, font=2, width=64):
    pixoo.send_text(text, xy, color, identifier, font, width)
    return 'OK'
