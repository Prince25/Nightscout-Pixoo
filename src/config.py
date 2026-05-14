import os
from dotenv import load_dotenv, find_dotenv

# Load the environment variables
dotenv_file = find_dotenv()
if not dotenv_file:
    raise FileNotFoundError('No .env file found.')
load_dotenv(dotenv_file, override=True)


# Environment variables
PIXOO_HOST = os.environ.get('PIXOO_HOST')
PIXOO_SCREEN_SIZE = int(os.environ.get('PIXOO_SCREEN_SIZE'))
PIXOO_RETRY_DELAY = os.environ.get('PIXOO_RETRY_DELAY')
NIGHTSCOUT_URL = os.environ.get('NIGHTSCOUT_URL')
CHANNEL_TIME = os.environ.get('CHANNEL_TIME')


# Validation
if "http" not in NIGHTSCOUT_URL:
    raise ValueError("NIGHTSCOUT_URL must start with 'http' or 'https'.")