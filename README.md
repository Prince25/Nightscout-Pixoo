# Nightscout -> Pixoo
This app displays blood glucose data from Nightscout to a Pixoo device.

<img alt="Image of Pixoo 64 running Nightscout -> Pixoo" src="https://i.imgur.com/NBu0EcV.jpeg" width="400">


## Introduction
**Nightscout -> Pixoo** makes use of the great [Pixoo Python library](https://github.com/SomethingWithComputers/pixoo) by [SomethingWithComputers](https://github.com/SomethingWithComputers); which offers various helpful features like automatic image conversion. :thumbsup:

Code inspiration from https://github.com/4ch1m/pixoo-rest


## Setup
Tested on Python 3.12.2

### Clone
Clone this repository:
```bash
git clone https://github.com/Prince25/Nightscout-Pixoo
```

### Configure Environmental Variables
See [`.env-example`](.env-example) for necessary variables. Rename `.env-example` or create an `.env` file and put your individual settings in it, especially for
```properties
NIGHTSCOUT_URL=
PIXOO_HOST=
```

- `NIGHTSCOUT_URL` is the URL to your Nightscout instance, e.g., `https://your-nightscout.herokuapp.com` or `http://192.168.1.116:4321` (IP:Port) if local.
- `PIXOO_HOST` is the IP address of your Pixoo device, e.g., `192.168.1.144`


## Usage
The app can now be run ...
* :snake: directly; using your existing (venv-)Python installation

or

* :package: fully packaged inside a dedicated (Docker-)container


### Direct

#### Initialize [Pixoo](https://github.com/SomethingWithComputers/pixoo) Submodule
```bash
git submodule init
git submodule update
```

#### Install Dependencies
Create a virtual environment and activate it (optional; but recommended):
```bash
python -m venv venv
. venv/bin/activate
venv\Scripts\activate (Windows)
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

#### Run
Finally, run the app:
```bash
python src/app.py
```

#### Troubleshooting
If you get the error `ModuleNotFoundError: No module named 'tkinter'` on Windows, look at [this](https://stackoverflow.com/a/59970646/13915206).


### Containerized
Simply execute ...
```bash
docker-compose up
```
... to automatically build the container and run it.


## License
Please read the [LICENSE](LICENSE) file.
