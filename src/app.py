from pixoo_helper import *
from urllib.parse import urljoin


NIGHTSCOUT_URL = os.environ.get('NIGHTSCOUT_URL')
NIGHTSCOUT_API = urljoin(NIGHTSCOUT_URL, '/api/v1/entries/sgv.json?count=2')
SCREEN_TIME = os.environ.get('SCREEN_TIME')
SCREEN_CENTER = (pixoo_screen_size - 1) // 2

# Hide TLS warnings: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Get JSON data from the API
def get_data_from_NS():
    while True:
        try:
            # print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Trying to get data from "{NIGHTSCOUT_URL}" ... ', end='')
            data = requests.get(NIGHTSCOUT_API, verify=False).json()
            
            # Parse the data
            current_sgv = str(data[0]['sgv'])
            current_direction = str(data[0]['direction'])
            delta_value = int(data[0]['sgv'] - data[1]['sgv'])
            delta = "+" if delta_value > 0 else ""
            delta += str(delta_value)
            # print('OK.')
            return current_sgv, current_direction, delta
        except Exception as error:
            print('FAILED. Sleeping' + retry_delay + 'seconds.')
            print('ERROR:', error)
            time.sleep(int(retry_delay))


# Draw NS data on Pixoo with optional border
def draw_NS(data, width=pixoo_screen_size - 1, height=pixoo_screen_size - 1, center=SCREEN_CENTER, border=False):
    current_sgv, current_direction, delta = data
    if border:
        draw_border(center - width // 2, center - height // 2, center + width // 2, center + height // 2)
    draw_text(current_sgv, center - 11 // 2, center - height // 3)
    if delta != "0":
        draw_text(delta, center - 3, center - 2)
    draw_arrow(current_direction, center - 7 // 2, center + 2 + height // 4, 6)


width = 20
height = 35
print("Running...")
while True:
    draw_fill()     # Clear the screen
    draw_border()   # Draw the border
    draw_text(datetime.now().strftime("%I:%M %p"), SCREEN_CENTER - 2 - 24//2, 6)
    draw_NS(get_data_from_NS(), width, height, SCREEN_CENTER, True)
    draw_text("ThePriniaCloud", 5, 54)
    # draw_pixel(SCREEN_CENTER, SCREEN_CENTER, 255, 0, 0)
    push()
    time.sleep(float(SCREEN_TIME))
    generic_set_number("channel", 1)    # Change to "Cloud" channel
    time.sleep(float(SCREEN_TIME))
    generic_set_number("channel", 0)    # Change to "Faces" channel
    time.sleep(float(SCREEN_TIME))



# length = 7
# draw_arrow('FortyFiveDown', 0, 0, length)
# draw_arrow('FortyFiveUp', 0, 20, length)
# draw_arrow('Flat', 0, 40, length)
# draw_arrow('SingleDown', 20, 0, length)
# draw_arrow('SingleUp', 20, 20, length)
# draw_arrow('DoubleDown', 40, 0, length)
# draw_arrow('564', 40, 40, length=length)
# draw_arrow('DoubleUp', 40, 20, length, push_now=True)


"""
Alternative way to get NS data
Take a screenshot of the NS page and draw it on Pixoo
or
https://github.com/4ch1m/pixoo-rest
"""

