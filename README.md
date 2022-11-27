# Whisper transcribe for vods

CUDA is highly recommended for this! It can run it on CPU, but oh boi, you don't want that.

## Installation

1. Create a python virtual environment

```bash
python -m venv venv
source venv/bin/activate # venv/Scripts/activate - if you use windows
```

2. Install pip packages

```bash
pip install -r requirements.txt
```

Head over to [pytorch.org](https://pytorch.org/get-started/locally/), select `Preview, OS, Pip, Python and latest CUDA version`. Then copy and paste the command to install pytorch.

3. Copy `SAMPLE_config.json` to `config.json` and change the api endpoints.

## Run

Just running the main script will mostly do all you need. Transcribed scripts will be saved in `transcripts/`.

```bash
python main.py
```

Using the large whisper model (`-m large`) will result in the best speech to text but requires ~12GB+ GPU memory and takes about twice as long as the medium model (which is default).

```
usage: main.py [-h] [-c CONFIG] [-o OUTPUT] [-m {medium,large}]

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config.json
  -o OUTPUT, --output OUTPUT
                        Directory where scripts will be saved
  -m {medium,large}, --model {medium,large}
                        Whisper model. Medium is default, but large will result in better quality
```
