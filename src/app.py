import sys
import signal
from config import NIGHTSCOUT_URL, PIXOO_HOST, PIXOO_SCREEN_SIZE
from integrations.pixoo import PixooDevice
from integrations.logger import setup_logging, log, teardown
from integrations.nightscout import NightscoutClient
from display.manager import DisplayManager


# Graceful shutdown handler to set Pixoo channel to "Cloud" when exiting
def _shutdown(pixoo_device):
    log("Shutting down...")
    try:
        pixoo_device.generic_set_number("channel", 1)  # Change to "Cloud" channel
        log('Setting channel to "Cloud".')
    except Exception as e:
        log(f"Shutdown error: {e}")
    
    teardown() # Clean up logging resources
    sys.exit(0)


def main():
    # Set up logging
    setup_logging()
    
    # Initialize clients and check connections
    ns_client = NightscoutClient(NIGHTSCOUT_URL)
    pixoo_device = PixooDevice(PIXOO_HOST, PIXOO_SCREEN_SIZE)
    
    # Shutdown handlers for graceful exit
    signal.signal(signal.SIGTERM, lambda s, f: _shutdown(pixoo_device))
    signal.signal(signal.SIGINT, lambda s, f: _shutdown(pixoo_device))

    try:
        ns_client.check_connection()
        pixoo_device.check_connection()
    except Exception as e:
        log(f"Failed to connect: {e}")
        return # Exit if we can't connect to either service

    # Initialize the DisplayManager with the Nightscout client and Pixoo device
    display_manager = DisplayManager(ns_client, pixoo_device)
    log("Running...")
    display_manager.run()


if __name__ == "__main__":
    main()
