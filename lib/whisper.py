import json
import os
import platform
from typing import Literal

import torch
from termcolor import colored

if platform.system() == "Darwin":
    from mlx_whisper import transcribe, writers
else:
    from faster_whisper import (BatchedInferencePipeline, WhisperModel,
                                format_timestamp)


class ArchivWhisperMac:
    def run(self, m4a: str, model: str, output: str, *args, **kwargs):
        print(colored("[mlx-whisper]", "blue"),
              f"Started: m4a={m4a}, model={model}")

        result = transcribe(
            audio=m4a,
            path_or_hf_repo=model,
            language="de",
            condition_on_previous_text=False,
            verbose=False)

        filename = os.path.splitext(m4a)[0]

        writer_txt = writers.get_writer(
            output_format="txt", output_dir=output)
        writer_txt(result, filename)

        writer_vtt = writers.get_writer(
            output_format="vtt", output_dir=output)
        writer_vtt(result, filename)

        writer_srt = writers.get_writer(
            output_format="srt", output_dir=output)
        writer_srt(result, filename)

        writer_json = writers.get_writer(
            output_format="json", output_dir=output)
        writer_json(result, filename)


class ArchivWhisper:
    def select_device(self, device: Literal["cuda", "cpu"] = "cuda") -> str:
        """sets the device being used by whisper. cuda or cpu"""
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
            print(colored(
                "CUDA IS NOT AVAILABLE! Whisper will run in CPU mode which is 3-4x slower... Please set up cuda.",
                "yellow"))
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
        batched_model = BatchedInferencePipeline(model=model)
        segments, info = batched_model.transcribe(
            m4a,
            vad_filter=True,
            log_progress=True,
            multilingual=True)

        filename = os.path.splitext(m4a)[0]
        final_json = {
            "text": "",
            "segments": [],
            "language": info.language
        }
        final_vtt = "WEBVTT\n"
        final_srt = ""

        for segment in segments:
            # json
            final_json["text"] += segment.text.strip() + "\n"
            segment_dict = segment._asdict()
            segment_dict.pop("words")
            segment_dict["text"] = segment.text.strip()
            final_json["segments"].append(segment_dict)

            # vtt
            final_vtt += "\n"
            final_vtt += f"{format_timestamp(segment.start)} --> {
                format_timestamp(segment.end)}\n"
            final_vtt += segment.text.strip() + "\n"

            # srt
            if final_srt != "":
                final_srt += "\n"
            final_srt += f"{segment.id}\n"
            final_srt += f"{format_timestamp(segment.start, True, ',')} --> {
                format_timestamp(segment.end, True, ',')}\n"
            final_srt += segment.text.strip() + "\n"

        with open(os.path.join(output, filename + ".json"), "w", encoding="utf-8") as f:
            json.dump(final_json, f)
        with open(os.path.join(output, filename + ".vtt"), "w", encoding="utf-8") as f:
            f.write(final_vtt)
        with open(os.path.join(output, filename + ".srt"), "w", encoding="utf-8") as f:
            f.write(final_srt)
        with open(os.path.join(output, filename + ".txt"), "w", encoding="utf-8") as f:
            f.write(final_json["text"])
