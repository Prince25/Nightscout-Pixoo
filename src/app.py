import atexit
from time import sleep
from datetime import datetime

from config import (
    CHANNEL_TIME,
    DEBUG,
    NIGHTSCOUT_URL,
    PIXOO_HOST,
    PIXOO_SCREEN_SIZE,
    SCREEN_CENTER,
)
from pixoo_helper import PixooDevice
from nightscout import NightscoutClient


# Graceful shutdown handler to set Pixoo channel to "Cloud" when exiting
def _shutdown(pixoo_device):
    pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Exiting. Setting channel to "Cloud".')


# Class to retrieve data from Nightscout and manage the display logic on the Pixoo device
class DisplayManager:
    def __init__(self, ns_client: NightscoutClient, pixoo_device: PixooDevice):
        self.ns_client = ns_client
        self.pixoo_device = pixoo_device
        self.width = 20
        self.height = 35
        self.arrow_length = 8

    # Draw the latest Nightscout data (SGV, direction, and delta) on the Pixoo display
    def draw_nightscout(self, border: bool = False):
        current_sgv, current_direction, delta = self.ns_client.get_latest_sgv()

        if border:
            self.pixoo_device.draw_border(
                SCREEN_CENTER - self.width // 2,
                SCREEN_CENTER - self.height // 2,
                SCREEN_CENTER + self.width // 2,
                SCREEN_CENTER + self.height // 2,
            )

        self.pixoo_device.draw_text(current_sgv, SCREEN_CENTER - 11 // 2, SCREEN_CENTER - self.height // 3)

        if delta != "0":
            self.pixoo_device.draw_text(delta, SCREEN_CENTER - 3, SCREEN_CENTER - 2)

        self.pixoo_device.draw_arrow(current_direction, SCREEN_CENTER - 7 // 2, SCREEN_CENTER, self.arrow_length)

    # Draw the current time
    def draw_clock(self):
        self.pixoo_device.draw_text(datetime.now().strftime("%I:%M %p"), SCREEN_CENTER - 2 - 24 // 2, 6)

    # Main loop to continuously update the display
    def run(self):
        while True:
            self.pixoo_device.draw_fill()  # Clear the screen

            if DEBUG:
                self.pixoo_device.debug_lines()

            self.pixoo_device.draw_border()  # Draw the outer frame
            self.draw_clock()
            self.draw_nightscout(border=True)

            if DEBUG:
                self.pixoo_device.debug_pixels()

            self.pixoo_device.push()

            sleep(float(CHANNEL_TIME))
            self.pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
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

