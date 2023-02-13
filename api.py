import os
import subprocess

import requests


class Api:
    def __init__(self, api: dict) -> None:
        """Set class variables"""
        self.api = api["url"]
        self.bearer = requests.post(
            f"https://{self.api}/token/new/", data=api["auth"]).json()["token"]

    def get_vods(self) -> list:
        """Get all vods from api"""
        req = requests.get(f"https://{self.api}/vods/?limit=-1")
        res = req.json()

        if res["error"] == True:
            print(f"Failed to get vods from {self.api}")
            print(req.text)
            exit(1)

        return res["result"]

    def download_vod(self, filename: str) -> None:
        """Download vod and extract acc track"""
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-i",
               f"https://{self.api}/media/vods/{filename}-segments/{filename}.m3u8", "-vn",
               "-c:a", "copy", "-bsf:a", "aac_adtstoasc", "-movflags", "frag_keyframe+empty_moov", "-y", f"{filename}.aac"]
        subprocess.check_output(cmd)

    def post_transcript(self, f: str) -> None:
        print("-"*20)
        filename = os.path.splitext(os.path.basename(f))[0]
        print(filename)
        with open(f, "r", encoding="utf-8") as txt:
            text = txt.read()

        newtext = []
        for line in text.splitlines():
            line = line.strip()
            if line.isdigit():
                continue
            newtext.append(line)

        uuid_req = requests.get(
            f"https://{self.api}/vods/?filename={filename}").json()
        if uuid_req["error"] == True:
            print("No vod for filename", filename)
            return
        uuid = uuid_req["result"][0]["uuid"]

        data = {
            "transcript": "\n".join(newtext)
        }
        header = {
            "Authorization": f"Bearer {self.bearer}"
        }
        req = requests.patch(
            f"https://{self.api}/vods/{uuid}", json=data, headers=header)
        if req.status_code != 200:
            print("error:", req.text)
            return
        else:
            print(req.text)
