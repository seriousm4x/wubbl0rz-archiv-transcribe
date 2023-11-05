import datetime
import json
import os
import pathlib

import meilisearch
from termcolor import colored


class ArchivMeili:
    def __init__(self, env: dict) -> None:
        print(colored("[meili]", "blue"), "Logging in to meili...")
        url = env["meili_url"]
        api_key = env["meili_master_key"]
        self.client = meilisearch.Client(url, api_key)

    def update_vods(self, vods: dict) -> None:
        """update or create vods"""
        print(colored("[meili]", "blue"), "Updating vods...")
        for vod in vods:
            del vod["created"]
            del vod["updated"]
            del vod["expand"]
            vod["date"] = int(datetime.datetime.strptime(
                vod["date"], "%Y-%m-%d %H:%M:%S.%fZ").timestamp())
        self.client.index("vods").update_documents(vods)

    def update_transcripts(self, vods: dict, output: pathlib.Path) -> None:
        """update or create transcripts"""
        print(colored("[meili]", "blue"), "Updating transcripts...")
        segments = []
        for vod in vods:
            json_path = os.path.join(output, vod["filename"] + ".json")
            if not os.path.exists(json_path):
                continue
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for segment in data["segments"]:
                segments.append({
                    "meili_id": f"{vod['id']}_{segment['id']}",
                    "id": vod["id"],
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "title": vod["title"],
                    "filename": vod["filename"],
                    "date": vod["date"],
                    "duration": vod["duration"],
                    "viewcount": vod["viewcount"]
                })
            if len(segments) > 50000:
                # avoid error "payload too large"
                print(colored("[meili]", "blue"),
                      f"Posting {len(segments)} segments")
                self.client.index("transcripts").update_documents(segments)
                segments = []
        if len(segments) > 0:
            print(colored("[meili]", "blue"),
                  f"Posting {len(segments)} segments")
            self.client.index("transcripts").update_documents(segments)
