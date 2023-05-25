import subprocess

import requests
from termcolor import colored


class ArchivApi:
    def __init__(self, env: dict) -> None:
        """Set class variables"""
        print(colored("[api]", "blue"), "Getting new api token...")
        self.api = env["api_url"]
        self.bearer = requests.post(
            f"{self.api}/token/new/", data=env["api_auth"]).json()["token"]

    def get_vods(self) -> list:
        """Get all vods from api"""
        print(colored("[api]", "blue"), "Getting all vods from api...")
        req = requests.get(f"{self.api}/vods/?limit=-1")
        res = req.json()
        if res["error"] == True:
            print(colored("[api]", "red"),
                  f"Failed to get vods from {self.api}")
            print(req.text)
            exit(1)
        return res["result"]

    def download_vod(self, filename: str) -> None:
        """Download vod and extract aac track"""
        print(colored("[api]", "blue"), f"Downloading vod...")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-i",
               f"{self.api}/media/vods/{filename}-segments/{filename}.m3u8", "-vn",
               "-c:a", "copy", "-bsf:a", "aac_adtstoasc", "-movflags",
               "frag_keyframe+empty_moov", "-y", f"{filename}.m4a"]
        subprocess.check_output(cmd)

    def get_clips(self) -> list:
        """Get all clips from api"""
        print(colored("[api]", "blue"), "Getting all clips from api...")
        req = requests.get(f"{self.api}/clips/?limit=-1")
        res = req.json()
        if res["error"] == True:
            print(colored("[api]", "red"),
                  f"Failed to get clips from {self.api}")
            print(req.text)
            exit(1)
        return res["result"]
