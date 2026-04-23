# Bust

Code for my face tracking cyber bust.


## Setup

The system requires 2 small screens, a raspberry pi 4b, and a picamea.


- `git clone git@github.com:camoverride/bust.git`
- `cd bust`
- `python -m venv --system-site-packages .venv` (system-site-packages so we get the picamera package.)
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `export DISPLAY=:0`
- `python track_faces.py`


## Run in Production

Start a service with systemd. This will start the program when the computer starts and revive it when it dies. This is expected to run on a Raspberry Pi 5 or Beelink running Ubuntu:

- `mkdir -p ~/.config/systemd/user`
- `cat bust.service > ~/.config/systemd/user/bust.service`

Start the service using the commands below:

- `systemctl --user daemon-reload`
- `systemctl --user enable bust.service`
- `systemctl --user start bust.service`

Start it on boot:

- `sudo loginctl enable-linger $(whoami)`

Get the logs:

- `journalctl --user -u bust.service`


## Increase System Longevity

Follow these steps in order:

    (1) Install tailscale for remote access and debugging.
    (2) Configure backup wifi networks.
    (3) Configure a Read-Only Overlay Filesystem
    (4) Set up periodic reboots (systemd).
