import os

import torch
from termcolor import colored
from whisper import load_model, transcribe
from whisper.utils import get_writer


class ArchivWhisper:
    def select_device(self) -> str:
        """sets the device being used by whisper. cuda or cpu"""
        device = "cuda"
        if not torch.cuda.is_available():
            device = "cpu"
            print(colored(
                "CUDA IS NOT AVAILABLE! Whisper will run in CPU mode which is incredibly slow... Please set up cuda.", "yellow"))
            reply = None
            while reply not in ["y", "n"]:
                reply = input(
                    "Do you want to continue? [y/n]: ").strip().casefold()
                if reply == "n":
                    exit(0)
        print(colored("[whisper]", "blue"), "Selected device:", device)
        return device

    def run(self, aac: str, model: str, device: str, output: str) -> None:
        """Transcribes all given vods to .txt .srt and .vtt"""
        print(colored("[whisper]", "blue"),
              f"Started: aac={aac}, model={model}, device={device}")
        model = load_model(model, device)
        # result = transcribe(model=model, audio=aac, beam_size=5,
        #                     best_of=5, verbose=False, language="de")

        # use condition_on_previous_text to help with larger segments of silence
        result = transcribe(model=model, audio=aac, beam_size=5,
                            best_of=5, verbose=False, language="de", condition_on_previous_text=False,
                            no_speech_threshold=0.3, compression_ratio_threshold=1.8)
        filename = os.path.splitext(aac)[0]

        writer = get_writer("json", output)
        writer(result, filename)

        writer = get_writer("txt", output)
        writer(result, filename)

        writer = get_writer("srt", output)
        writer(result, filename)

        writer = get_writer("vtt", output)
        writer(result, filename)
