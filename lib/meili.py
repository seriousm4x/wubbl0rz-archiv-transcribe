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
            vod["date"] = int(datetime.datetime.fromisoformat(
                vod["date"]).timestamp())
            if vod.get("clips"):
                del vod["clips"]
            if vod.get("publish"):
                del vod["publish"]
        self.client.index("vods").update_documents(vods, "uuid")

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
                    "id": f"{vod['uuid']}_{segment['id']}",
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "vod": vod["uuid"],
                    "title": vod["title"],
                    "filename": vod["filename"],
                    "date": vod["date"],
                    "duration": vod["duration"],
                    "viewcount": vod["viewcount"]
                })
            if len(segments) > 10000:
                # avoid error "payload too large"
                self.client.index("transcripts").update_documents(segments)
                segments = []
        self.client.index("transcripts").update_documents(segments)

    def update_clips(self, clips: dict) -> None:
        """update or create clips"""
        print(colored("[meili]", "blue"), "Updating clips...")
        clips_to_post = []
        for clip in clips:
            clip["date"] = int(datetime.datetime.fromisoformat(
                clip["date"]).timestamp())
            if clip.get("creator"):
                del clip["creator"]
            if clip.get("game"):
                del clip["game"]
            if clip.get("vod"):
                del clip["vod"]
            clips_to_post.append(clip)
            if len(clips_to_post) > 10000:
                # avoid error "payload too large"
                self.client.index('clips').update_documents(clips_to_post, "uuid")
                clips_to_post = []
        self.client.index('clips').update_documents(clips_to_post, "uuid")
