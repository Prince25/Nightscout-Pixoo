import atexit
from datetime import datetime
from config import NIGHTSCOUT_URL, PIXOO_HOST, PIXOO_SCREEN_SIZE
from integrations.pixoo import PixooDevice
from integrations.nightscout import NightscoutClient
from display.manager import DisplayManager


# Graceful shutdown handler to set Pixoo channel to "Cloud" when exiting
def _shutdown(pixoo_device):
    pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Exiting. Setting channel to "Cloud".')


def main():
    # Initialize clients and check connections
    ns_client = NightscoutClient(NIGHTSCOUT_URL)
    pixoo_device = PixooDevice(PIXOO_HOST, PIXOO_SCREEN_SIZE)
    atexit.register(_shutdown, pixoo_device)

    try:
        ns_client.check_connection()
        pixoo_device.check_connection()
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to connect: {e}")
        return # Exit if we can't connect to either service

    # Initialize the DisplayManager with the Nightscout client and Pixoo device
    display_manager = DisplayManager(ns_client, pixoo_device)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Running...")
    display_manager.run()


if __name__ == "__main__":
    main()
