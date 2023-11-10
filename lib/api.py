import subprocess

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
        """Download vod and extract aac track"""
        print(colored("[api]", "blue"), f"Downloading vod...")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-i",
               f"{self.api}/vods/{filename}-segments/{filename}.m3u8", "-vn",
               "-c:a", "copy", "-bsf:a", "aac_adtstoasc", "-movflags",
               "frag_keyframe+empty_moov", "-y", f"{filename}.m4a"]
        subprocess.check_output(cmd)
