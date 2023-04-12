import os
import pathlib

from git import Repo
from termcolor import colored


class ArchivGit:
    def __init__(self) -> None:
        self.repo = Repo(os.path.join(pathlib.Path(
            __file__).parent.parent.resolve(), ".git"))
        self.origin = self.repo.remote(name="origin")

    def pull(self) -> None:
        """git pull"""
        print(colored("[git]", "blue"), "pull...")
        self.origin.pull()

    def push(self, commit_msg: str, add_files: pathlib.Path) -> None:
        """git push"""
        print(colored("[git]", "blue"), "push...")
        try:
            self.repo.git.add(add_files)
            self.repo.index.commit(commit_msg)
            self.origin.push()
        except Exception as e:
            print(colored("[git]", "red"), "Git error:")
            print(e)
