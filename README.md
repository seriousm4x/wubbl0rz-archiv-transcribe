# Whisper transcribe for vods

CUDA is highly recommended for this! CPU is about 3x slower. Read more about speed comparison here: https://github.com/guillaumekln/faster-whisper#benchmark

## Installation

1. Create a python virtual environment

```bash
python -m venv venv

source venv/bin/activate # linux, or...
venv/Scripts/activate # for windows
```

2. Install pip packages

```bash
pip install -r requirements.txt
```

Head over to [pytorch.org](https://pytorch.org/get-started/locally/), select:

<table>
    <tr>
        <td>PyTorch Build</td>
        <td>Stable</td>
    </tr>
    <tr>
        <td>Your OS</td>
        <td>xxxx</td>
    </tr>
    <tr>
        <td>Package</td>
        <td>Pip</td>
    </tr>
    <tr>
        <td>Language</td>
        <td>Python</td>
    </tr>
    <tr>
        <td>Compute Platform</td>
        <td>CUDA &lt;latest version&gt;</td>
    </tr>
</table>

Then run the given command to install pytorch.

3. Copy `SAMPLE_config.json` to `config.json` and change the api endpoints.

4. Make sure to have `ffmpeg` installed.

## Run

Just running the main script will mostly do all you need. Transcribed scripts will be saved in `transcripts/`.

```bash
python main.py -e prod transcribe
```

Using the large whisper model (default) will result in the best speech to text and requires ~6GB GPU memory. Use `python main.py transcribe -h` so see all available models.

```
usage: Wubbl0rz Archiv Transcribe [-h] [-c CONFIG] -e {prod,dev} [-o OUTPUT]
                                  {transcribe,post} ...

positional arguments:
  {transcribe,post}     Available commands
    transcribe          Run whisper to transcribe vods to text
    post                Post available transcriptions

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config.json
  -e {prod,dev}, --environment {prod,dev}
                        Target environment
  -o OUTPUT, --output OUTPUT
                        Output directory for transcripts
```
