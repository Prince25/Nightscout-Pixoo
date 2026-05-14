import atexit
from pixoo_helper import *
from config import NIGHTSCOUT_URL, CHANNEL_TIME
from urllib.parse import urljoin


# Hide TLS warnings: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Set channel to "Cloud" on exit
@atexit.register
def exit():
    generic_set_number("channel", 1)    # Change to "Cloud" channel
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Exiting: setting channel to "Cloud".')


SCREEN_CENTER = (PIXOO_SCREEN_SIZE - 1) // 2
DEBUG = False


# Get JSON data from the API
def get_data_from_NS():
    while True:
        try:
            NIGHTSCOUT_API = urljoin(NIGHTSCOUT_URL, '/api/v1/entries/sgv.json?count=2')
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
            print('FAILED. Sleeping' + PIXOO_RETRY_DELAY + 'seconds.')
            print('ERROR:', error)
            time.sleep(int(PIXOO_RETRY_DELAY))


# Draw NS data on Pixoo with optional border
def draw_NS(data, width=PIXOO_SCREEN_SIZE - 1, height=PIXOO_SCREEN_SIZE - 1, center=SCREEN_CENTER, border=False):
    current_sgv, current_direction, delta = data
    if border:
        draw_border(center - width // 2, center - height // 2, center + width // 2, center + height // 2)
    draw_text(current_sgv, center - 11 // 2, center - height // 3)
    if delta != "0":
        draw_text(delta, center - 3, center - 2)
    draw_arrow("DoubleUp", center - 7 // 2, center, 8)


width = 20
height = 35
print("Running...")
while True:
    draw_fill()     # Clear the screen
    if DEBUG:
        debug_lines()
    draw_border()   # Draw the border
    draw_text(datetime.now().strftime("%I:%M %p"), SCREEN_CENTER - 2 - 24//2, 6)
    draw_NS(get_data_from_NS(), width, height, SCREEN_CENTER, True)
    if DEBUG:
        debug_pixels()
    push()
    time.sleep(float(CHANNEL_TIME))
    generic_set_number("channel", 1)    # Change to "Cloud" channel
    time.sleep(float(CHANNEL_TIME))
    generic_set_number("channel", 0)    # Change to "Faces" channel
    time.sleep(float(CHANNEL_TIME))

