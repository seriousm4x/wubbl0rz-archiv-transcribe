import argparse
import json
import os
import pathlib
import time
from datetime import timedelta
from typing import Any, Optional

from termcolor import colored

from lib.transcribe import ArchivWhisper
from lib.api import ArchivApi
from lib.git import ArchivGit
from lib.meili import ArchivMeili


def read_config() -> Any:
    """Read config file from args"""
    print(colored("[main]", "blue"), "Reading config...")
    with open(args.config, "r", encoding="utf-8") as f:
        return json.load(f)


def run_transcribe():
    """Compare vods in api with files in output dir and transcribe missing vods"""
    # read config from args
    config = read_config()

    # keep out transcripts up to date
    git = ArchivGit()
    git.pull()

    # get vods in api
    api = ArchivApi(config[args.environment])
    all_vods_in_api = api.get_vods()

    # compare with local files
    vods_to_transcribe = []
    for vod in all_vods_in_api:
        if not os.path.exists(os.path.join(args.output, vod["filename"] + ".json")):
            vods_to_transcribe.append(vod)

    # print result and exit if no vods
    print(colored("[main]", "blue"), len(vods_to_transcribe), "vods to transcribe")
    if len(vods_to_transcribe) == 0:
        exit(0)

    # get the device to run whisper on
    whisper = ArchivWhisper()
    whisper_device = whisper.select_device()

    # transcribe each vod
    i = 0
    for vod in vods_to_transcribe:
        i += 1
        start = time.time()
        filename = vod["filename"]
        aac = f"{filename}.aac"
        print(colored("[main]", "blue"), i, "of", len(vods_to_transcribe), filename)

        # download vod and extract audio to aac, transcribe audio and delete aac afterwards
        api.download_vod(filename)
        whisper.run(aac=aac, model=args.model,
                               device=whisper_device, output=args.output)
        os.remove(aac)

        # push transcript to git
        git.pull()
        git.push(f"[🤖] add {vod['filename']}", args.output)

        # some console output
        end = time.time()
        print(colored("[main]", "green"), "Finished in:", timedelta(seconds=end-start))
        print("")

    # show final message
    if len(vods_to_transcribe) == 1:
        print(colored("[main]", "green"), f"Transcribed {len(vods_to_transcribe)} file")
    else:
        print(colored("[main]", "green"), f"Transcribed {len(vods_to_transcribe)} files")

    # ask to post vods to meilisearch
    reply = None
    while reply not in ["y", "n"]:
        reply = input(
            "Post transcripts to meilisearch? [y/n]: ").strip().casefold()
        if reply == "y":
            run_post(vods_to_transcribe)


def run_post(vods_to_post: Optional[list] = None) -> None:
    """Post transcriptions, vods and clips to meilisearch"""
    # read config from args
    config = read_config()

    api = ArchivApi(config[args.environment])
    clips_to_post = api.get_clips()
    if not vods_to_post:
        # get vods in api
        vods_to_post = api.get_vods()

    # run meilisearch
    meili = ArchivMeili(config[args.environment])
    meili.update_vods(vods_to_post)
    meili.update_transcripts(vods_to_post, args.output)
    meili.update_clips(clips_to_post)


def main() -> None:
    if args.cmd == "transcribe":
        run_transcribe()
    elif args.cmd == "post":
        run_post()


if __name__ == "__main__":
    # main parser
    parser = argparse.ArgumentParser(prog="Wubbl0rz Archiv Transcribe")
    parser.add_argument("-c", "--config", help="Path to config.json", default=os.path.join(
        pathlib.Path(__file__).parent.resolve(), "config.json"), type=pathlib.Path)
    parser.add_argument("-e", "--environment", choices=[
                        "prod", "dev"], required=True, type=str, help="Target environment")
    parser.add_argument("-o", "--output", default=os.path.join(pathlib.Path(__file__).parent.resolve(),
                        "transcripts"), type=pathlib.Path, help="Output directory for transcripts")
    subparsers = parser.add_subparsers(
        dest="cmd", help="Availble commands")

    # parser for transcibe
    transcribe_parser = subparsers.add_parser(
        "transcribe",  help="Run whisper to transcribe vods to text")
    transcribe_parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"],
                                   default="medium", type=str, help="Whisper language model")

    # parser for post
    post_parser = subparsers.add_parser(
        "post",  help="Post available transcriptions")

    # run parse
    args = parser.parse_args()
    main()
