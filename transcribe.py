import os

import torch
from whisper import load_model, transcribe
from whisper.utils import write_srt, write_txt, write_vtt


def select_whisper_device() -> str:
    """sets the device being used by whisper. cuda or cpu"""
    device = "cuda"
    if not torch.cuda.is_available():
        device = "cpu"
        print("CUDA IS NOT AVAILABLE! Whisper will run in CPU mode which is incredibly slow... Please set up cuda.")
        reply = None
        while reply not in ["y", "n"]:
            reply = input(
                "Do you want to continue? [y/n]: ").strip().casefold()
            if reply == "n":
                exit(0)
    return device


def run_whisper(aac: str, model: str, device: str, output: str) -> None:
    """Transcribes all given vods to .txt .srt and .vtt"""
    model = load_model(model, device)
    result = transcribe(model=model, audio=aac, beam_size=5,
                        best_of=5, verbose=False, language="de")
    filename = os.path.splitext(aac)[0]

    with open(os.path.join(output, filename + ".txt"), "w", encoding="utf-8") as f:
        write_txt(result["segments"], file=f)

    with open(os.path.join(output, filename + ".srt"), "w", encoding="utf-8") as f:
        write_srt(result["segments"], file=f)

    with open(os.path.join(output, filename + ".vtt"), "w", encoding="utf-8") as f:
        write_vtt(result["segments"], file=f)
