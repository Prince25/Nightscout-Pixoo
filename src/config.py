import os
from dotenv import load_dotenv, find_dotenv

# Load the environment variables
dotenv_file = find_dotenv()
if not dotenv_file:
    raise FileNotFoundError('No .env file found.')
load_dotenv(dotenv_file, override=True)

# Convert hex to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Environment variables
PIXOO_HOST = os.environ.get('PIXOO_HOST')
PIXOO_SCREEN_SIZE = int(os.environ.get('PIXOO_SCREEN_SIZE'))
NIGHTSCOUT_URL = os.environ.get('NIGHTSCOUT_URL')
CHANNEL_TIME = os.environ.get('CHANNEL_TIME')
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# Glucose thresholds
GLUCOSE_URGENT_LOW = int(os.environ.get('GLUCOSE_URGENT_LOW', 55))
GLUCOSE_LOW = int(os.environ.get('GLUCOSE_LOW', 90))
GLUCOSE_NORMAL_MAX = int(os.environ.get('GLUCOSE_NORMAL_MAX', 150))
GLUCOSE_HIGH = int(os.environ.get('GLUCOSE_HIGH', 300))


# Color thresholds
COLOR_URGENT_LOW = hex_to_rgb(os.environ.get('COLOR_URGENT_LOW', '#FF0000'))
COLOR_LOW = hex_to_rgb(os.environ.get('COLOR_LOW', '#FFFF00'))
COLOR_NORMAL = hex_to_rgb(os.environ.get('COLOR_NORMAL', '#FFFFFF'))
COLOR_HIGH = hex_to_rgb(os.environ.get('COLOR_HIGH', '#FF9900'))
COLOR_URGENT_HIGH = hex_to_rgb(os.environ.get('COLOR_URGENT_HIGH', '#FF0000'))


# Global constants
SCREEN_CENTER = PIXOO_SCREEN_SIZE // 2


# Validation
if "http" not in NIGHTSCOUT_URL:
    raise ValueError("NIGHTSCOUT_URL must start with 'http' or 'https'.")
