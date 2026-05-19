# Nightscout -> Pixoo
This app displays blood glucose data from Nightscout to a Pixoo device. Now with two layouts and glucose-based colors!

| Layout version 1 | Layout version 2 (Default) |
| :---: | :---: |
| <img alt="Image of Pixoo 64 running Nightscout -&gt Pixoo" src="https://i.imgur.com/5juNvKP.jpeg" width="400" /> | <img alt="Image of Pixoo 64 running Nightscout -&gt Pixoo" src="https://i.imgur.com/2EYOGjO.jpeg" width="400" /> |

**Nightscout -> Pixoo** makes use of the great [Pixoo Python library](https://github.com/SomethingWithComputers/pixoo); which offers various helpful features like automatic image conversion. :thumbsup:


## Usage
This app can be run in two ways:

* :snake: Directly with Python
* :package: Using Docker Compose

Tested on Python 3.13.5

### Direct

#### Clone
Clone this repository:
```bash
git clone https://github.com/Prince25/Nightscout-Pixoo
```

#### Initialize Pixoo submodule
```bash
git submodule init
git submodule update
```

#### Install dependencies
Create a virtual environment and activate it (optional, but recommended):
```bash
python -m venv venv
. venv/bin/activate (Linux)
venv\Scripts\activate (Windows)
```

Install dependencies:
```bash
pip install -r requirements.txt
```

#### Configure environmental variables
Copy the example file and update it with your own settings:

```bash
cp .env-example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env-example .env
```

The app reads configuration from `.env` in the repository root.

See [environment variables](#environment-variables) section for details.

#### Run
```bash
python src/app.py
```


### Docker Compose
See [`docker-compose.yml`](docker-compose.yml) for containerized deployment.

Define [environment variables](#environment-variables) to your liking, especially `NIGHTSCOUT_URL` and `PIXOO_HOST`.

Run the container with:

```bash
docker-compose up
```


### Environment variables
| Variable | Default | Description |
| --- | --- | --- |
| `NIGHTSCOUT_URL` | | Nightscout instance URL, e.g. `https://your-nightscout.herokuapp.com` or `http://192.168.1.116:4321`. |
| `PIXOO_HOST` | | Pixoo device IP address, e.g. `192.168.1.144`. |
| `PIXOO_SCREEN_SIZE` | `64` | Pixoo screen size. Use `64` for Pixoo 64 devices. |
| `CHANNEL_TIME` | `15` | Seconds to show each display channel before refreshing or switching. |
| `LAYOUT` | `v2` | Display layout version. Use `v2` or `v1` depending on the screen layout you want. |
| `SHOW_CLOUD` | `True` | Switch to the "cloud" channel as per Divoom app. Set to `False` to hide it. |
| `SHOW_FACES` | `False` | Switch to the "face" channel as chosen in the Divoom app. Set to `False` to hide it. |
| `GLUCOSE_URGENT_LOW` | `55` | SGV threshold for urgent low glucose. |
| `GLUCOSE_LOW` | `90` | SGV threshold for low glucose. |
| `GLUCOSE_NORMAL_MAX` | `150` | Maximum SGV value considered normal. |
| `GLUCOSE_HIGH` | `300` | SGV threshold for high glucose. |
| `COLOR_URGENT_LOW` | `#FF0000` (Red) | Color used for urgent low glucose. |
| `COLOR_LOW` | `#FFFF00` (Yellow) | Color used for low glucose. |
| `COLOR_NORMAL` | `#FFFFFF` (White) | Color used for normal glucose. |
| `COLOR_HIGH` | `#FF9900` (Orange) | Color used for high glucose. |
| `COLOR_URGENT_HIGH` | `#FF0000` (Red) | Color used for urgent high glucose. |


## Troubleshooting
If you get `ModuleNotFoundError: No module named 'tkinter'` on Windows, look at [this](https://stackoverflow.com/a/59970646/13915206).


## License
[Attribution-NonCommercial-ShareAlike 4.0 International](LICENSE)
