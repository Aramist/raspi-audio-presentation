<div id="top"></div>

<!-- ABOUT THE PROJECT -->
## About The Project

This is a lightweight script that controls the presentation of different sounds through a speaker connected to a Raspberry Pi through a hat-mounted sound card (HifiBerry AMP2). Audio presentations are prescheduled to avoid any drift in presentation time due to I/O. Additionally, a square signal of configurable length is sent through one of the Pi's GPIO ports just before the onset of the sound.

<!-- GETTING STARTED -->
## Getting Started

At the moment, the raspi portion of this setup is very lightweight and the setup instructions reflect that:

### Prerequisites

* pyaudio
  ```sh
  sudo apt install portaudio19-dev -y
  python3 -m pip install pyaudio
  ```

* scipy/numpy (for reading wav files)
  ```sh
  python3 -m pip install scipy numpy
  ```

* Earlier versions of the script relied on SoX:
  ```sh
  sudo apt install sox -y
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Aramist/raspi-audio-presentation.git
   ```
2. Modify audio\_config.py as necessary
   ```sh
   vim audio_config.py
   ```
3. Run audio\_presentation.py
   ```sh
   python3 audio_presentation.py
   ```

