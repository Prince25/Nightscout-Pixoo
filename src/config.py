import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Load the environment variables
try:
    dotenv_file = find_dotenv()
    if not dotenv_file:
        raise FileNotFoundError('No .env file found.')
    load_dotenv(dotenv_file, override=True)
except Exception as e:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to load environment: {e}")
    raise

# Convert hex to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Environment variables
try:
    NIGHTSCOUT_URL = os.environ.get('NIGHTSCOUT_URL')
    PIXOO_HOST = os.environ.get('PIXOO_HOST')
    PIXOO_SCREEN_SIZE = int(os.environ.get('PIXOO_SCREEN_SIZE', 64)) # Default to 64 if not set
    CHANNEL_TIME = os.environ.get('CHANNEL_TIME', 15)  # Default to 15 seconds if not set
    LAYOUT = os.environ.get('LAYOUT', 'v2')  # Default to v2 if not set
    SHOW_CLOUD = os.environ.get('SHOW_CLOUD', 'True').lower() in ('true', '1', 'yes')
    SHOW_FACES = os.environ.get('SHOW_FACES', 'False').lower() in ('true', '1', 'yes')
except Exception as e:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to parse environment variables: {e}")
    raise


# Glucose thresholds
try:
    GLUCOSE_URGENT_LOW = int(os.environ.get('GLUCOSE_URGENT_LOW', 55))
    GLUCOSE_LOW = int(os.environ.get('GLUCOSE_LOW', 90))
    GLUCOSE_NORMAL_MAX = int(os.environ.get('GLUCOSE_NORMAL_MAX', 150))
    GLUCOSE_HIGH = int(os.environ.get('GLUCOSE_HIGH', 300))
except Exception as e:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to parse glucose thresholds: {e}")
    raise


# Color thresholds
try:
    COLOR_URGENT_LOW = hex_to_rgb(os.environ.get('COLOR_URGENT_LOW', '#FF0000'))
    COLOR_LOW = hex_to_rgb(os.environ.get('COLOR_LOW', '#FFFF00'))
    COLOR_NORMAL = hex_to_rgb(os.environ.get('COLOR_NORMAL', '#FFFFFF'))
    COLOR_HIGH = hex_to_rgb(os.environ.get('COLOR_HIGH', '#FF9900'))
    COLOR_URGENT_HIGH = hex_to_rgb(os.environ.get('COLOR_URGENT_HIGH', '#FF0000'))
except Exception as e:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Failed to parse color thresholds: {e}")
    raise


# Global constants
SCREEN_CENTER = PIXOO_SCREEN_SIZE // 2


# Validation
try:
    # Validate NIGHTSCOUT_URL
    if not NIGHTSCOUT_URL:
        raise ValueError("NIGHTSCOUT_URL is not set.")
    if not (NIGHTSCOUT_URL.startswith("http://") or NIGHTSCOUT_URL.startswith("https://")):
        raise ValueError("NIGHTSCOUT_URL must start with 'http://' or 'https://'.")

    # Validate PIXOO_HOST
    if not PIXOO_HOST:
        raise ValueError("PIXOO_HOST is not set.")
    # Basic hostname/ip check: allow 'localhost', hostnames containing a dot, or numeric IPs
    host_ok = (
        PIXOO_HOST == 'localhost'
        or '.' in PIXOO_HOST
        or all(part.isdigit() for part in PIXOO_HOST.replace(':','').split('.'))
    )
    if not host_ok:
        raise ValueError("PIXOO_HOST does not look like a valid hostname or IP.")
except Exception as e:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Config error: {e}")
    raise
