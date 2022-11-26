import argparse
import json
import os
import pathlib
import time
from datetime import timedelta

from git import Repo

import transcribe
from api import Api


def process_vods() -> list:
    """Transcribe all needed vods and push them to git"""
    # use the first api in config to transcribing and set whisper device
    first_api = Api(config["apis"][0])
    device = transcribe.select_whisper_device()

    # only use vods where no transcript exists
    vods = first_api.get_vods()
    vods = [vod for vod in vods if not os.path.exists(
        os.path.join(args.output, f"{vod['filename']}.srt"))]
    count = len(vods)

    i = 0
    for vod in vods:
        i += 1
        start = time.time()
        filename = vod["filename"]
        aac = f"{filename}.aac"
        print(i, "of", count, filename)

        # download vod and extract audio to aac, transcribe audio and delete aac afterwards
        print("Downloading vod...")
        first_api.download_vod(filename)
        print("Transcribing...")
        transcribe.run_whisper(aac=aac, model=args.model,
                               device=device, output=args.output)
        os.remove(aac)

        # push transcript to git
        try:
            repo = Repo(os.path.join(pathlib.Path(
                __file__).parent.resolve(), ".git"))
            origin = repo.remote(name="origin")
            origin.pull()
            repo.git.add(args.output)
            repo.index.commit(f"[🤖] add {vod['filename']}")
            origin.push()
        except Exception as e:
            print("Git error:", e)

        end = time.time()
        print("Finished in:", timedelta(seconds=end-start))
        print("-"*20)

    if count == 1:
        print(f"Transcribed {count} file")
    else:
        print(f"Transcribed {count} files")

    return vods


def post_vods(vods) -> None:
    """Post all given vods to all apis in config"""
    for ap in config["apis"]:
        a = Api(ap)
        for vod in vods:
            a.post_transcript(os.path.join(
                args.output, vod["filename"] + ".srt"))


def main() -> None:
    vods = process_vods()
    if len(vods) == 0:
        exit(0)

    print("Please transfer the transcripts to all your servers in the config before posting files to api.")
    reply = None
    while reply not in ["y", "n"]:
        reply = input("Continue? [y/n]: ").strip().casefold()
        if reply == "n":
            exit(0)
    post_vods(vods)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Path to config.json', default=os.path.join(pathlib.Path(__file__).parent.resolve(), "config.json"), type=pathlib.Path)
    parser.add_argument(
        '-o', '--output', help='Directory where scripts will be saved', default=os.path.join(pathlib.Path(__file__).parent.resolve(), "transcripts"), type=pathlib.Path)
    parser.add_argument(
        '-m', '--model', help='Whisper model. Medium is default, but large will result in better quality.', choices=["medium", "large"], default="medium", type=str)
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("Config file doesn't exist")
        print("Please use SAMPLE_config.json, rename it to config.json and edit your api endpoints.")
        exit(1)

    if not os.path.isdir(args.output):
        print("Output path doesn't exist. I'll create it...")
        os.mkdir(args.output)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    if config["version"] != "1.0":
        print("Config doesn't have the latest version. Please update it.")
        exit(1)

    if len(config["apis"]) == 0:
        print("Config doesn't have an api. Please add at least one.")
        exit(1)

    main()
