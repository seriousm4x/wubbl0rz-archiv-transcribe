import json
import os

import torch
from faster_whisper import WhisperModel, format_timestamp
from termcolor import colored
from tqdm import tqdm


class ArchivWhisper:
    def select_device(self) -> str:
        """sets the device being used by whisper. cuda or cpu"""
        device = "cuda"
        if not torch.cuda.is_available():
            device = "cpu"
            print(colored(
                "CUDA IS NOT AVAILABLE! Whisper will run in CPU mode which is 3-4x slower... Please set up cuda.", "yellow"))
            reply = None
            while reply not in ["y", "n"]:
                reply = input(
                    "Do you want to continue? [y/n]: ").strip().casefold()
                if reply == "n":
                    exit(0)
        print(colored("[whisper]", "blue"), "Selected device:", device)
        return device

    def run(self, m4a: str, model: str, device: str, output: str) -> None:
        """Transcribes all given vods to .txt .srt and .vtt"""
        print(colored("[whisper]", "blue"),
              f"Started: m4a={m4a}, model={model}, device={device}")

        model = WhisperModel(model_size_or_path=model, device=device)
        segments, info = model.transcribe(
            m4a, language="de", no_speech_threshold=0.3, condition_on_previous_text=False)

        filename = os.path.splitext(m4a)[0]
        final_json = {
            "text": "",
            "segments": [],
            "language": info.language
        }
        final_vtt = "WEBVTT\n"
        final_srt = ""

        with tqdm(total=info.duration, unit="sec", bar_format="{l_bar}{bar} | {n:0.1f}/{total:0.1f} [{elapsed}<{remaining}, {rate_fmt}{postfix}]") as pbar:
            for segment in segments:
                pbar.update(segment.end - pbar.n)

                # json
                final_json["text"] += segment.text.strip() + "\n"
                segment_dict = segment._asdict()
                segment_dict.pop("words")
                segment_dict["text"] = segment.text.strip()
                final_json["segments"].append(segment_dict)

                # vtt
                final_vtt += "\n"
                final_vtt += f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n"
                final_vtt += segment.text.strip() + "\n"

                # srt
                if final_srt != "":
                    final_srt += "\n"
                final_srt += f"{segment.id}\n"
                final_srt += f"{format_timestamp(segment.start, True, ',')} --> {format_timestamp(segment.end, True, ',')}\n"
                final_srt += segment.text.strip() + "\n"
            pbar.n = pbar.total

        with open(os.path.join(output, filename + ".json"), "w", encoding="utf-8") as f:
            json.dump(final_json, f)
        with open(os.path.join(output, filename + ".vtt"), "w", encoding="utf-8") as f:
            f.write(final_vtt)
        with open(os.path.join(output, filename + ".srt"), "w", encoding="utf-8") as f:
            f.write(final_srt)
        with open(os.path.join(output, filename + ".txt"), "w", encoding="utf-8") as f:
            f.write(final_json["text"])
