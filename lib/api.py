import requests

from pocketbase import PocketBase
from termcolor import colored


class ArchivApi:
    def __init__(self, env: dict) -> None:
        """Set class variables"""
        print(colored("[api]", "blue"), "Connecting to pocketbase...")
        self.api = env["api_url"]
        self.client = PocketBase(self.api)

    def get_vods(self) -> list:
        """Get all vods from api"""
        print(colored("[api]", "blue"), "Getting all vods from api...")
        vods = []
        page = 1
        while True:
            result = self.client.collection("vod").get_list(page, 500, {
                "fields": "id,title,duration,date,viewcount,filename,resolution,fps,size"
            })
            vods = vods + [x.__dict__ for x in result.items]
            if result.page == result.total_pages:
                return vods
            page += 1

    def download_vod(self, filename: str) -> None:
        """Download audio track of vod"""
        print(colored("[api]", "blue"), "Downloading audio...")
        url = f"{self.api}/download/vod/{filename}?audio=true"
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(f"{filename}.ogg", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
