import argparse
import json
import os
import pathlib
import time
from datetime import timedelta
from typing import Any, Optional

from termcolor import colored

from lib.api import ArchivApi
from lib.git import ArchivGit
from lib.meili import ArchivMeili
from lib.whisper import ArchivWhisper


def read_config() -> Any:
    """Read config file from args"""
    print(colored("[main]", "blue"), "Reading config...")
    with open(args.config, "r", encoding="utf-8") as f:
        conf = json.load(f)
        if conf["version"] != "3":
            print(colored("[main]", "red"),
                  "Config file has wrong version. Please update it.")
            exit(1)
        return conf


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
    print(colored("[main]", "blue"), len(
        vods_to_transcribe), "vods to transcribe")
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
        m4a = f"{filename}.m4a"
        print(colored("[main]", "blue"), i, "of",
              len(vods_to_transcribe), filename)

        # download vod and extract audio to m4a, transcribe audio and delete m4a afterwards
        api.download_vod(filename)
        whisper.run(m4a=m4a, model=args.model,
                    device=whisper_device, output=args.output)
        os.remove(m4a)

        # push transcript to git
        git.pull()
        git.push(f"[🤖] add {vod['filename']}", args.output)

        # some console output
        end = time.time()
        print(colored("[main]", "green"), "Finished in:",
              timedelta(seconds=end-start))

    # show final message
    if len(vods_to_transcribe) == 1:
        print(colored("[main]", "green"),
              f"Transcribed {len(vods_to_transcribe)} file")
    else:
        print(colored("[main]", "green"),
              f"Transcribed {len(vods_to_transcribe)} files")

    # post vods to meilisearch
    run_post(vods_to_transcribe)


def run_post(vods_to_post: Optional[list] = None) -> None:
    """Post transcriptions and vods to meilisearch"""
    # read config from args
    config = read_config()

    api = ArchivApi(config[args.environment])
    if not vods_to_post:
        # get vods in api
        vods_to_post = api.get_vods()

    # run meilisearch
    meili = ArchivMeili(config[args.environment])
    meili.update_vods(vods_to_post)
    meili.update_transcripts(vods_to_post, args.output)


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
        dest="cmd", help="Available commands")

    # parser for transcibe
    transcribe_parser = subparsers.add_parser(
        "transcribe",  help="Run whisper to transcribe vods to text")
    transcribe_parser.add_argument("-m", "--model", choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en",
                                   "medium", "medium.en", "large-v1", "large-v2", "large-v3"], default="large-v3",
                                   type=str, help="Whisper language model")

    # parser for post
    post_parser = subparsers.add_parser(
        "post",  help="Post available transcriptions")

    # run parse
    args = parser.parse_args()
    main()
