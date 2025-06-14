from pathlib import Path
from typing import List
from debug_tools import attach_context

import debug_tools


class File:
    lines: List[str]

    def __init__(self, fullpath: Path):
        if not fullpath.is_file():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a file"))
        self.fullpath = fullpath  # Path relative to Project's root DIR
        self.lines = []

    @property
    def name(self) -> str:
        return self.fullpath.name


class Directory:
    files: List['File']
    dirs: List['Directory']

    def __init__(self, fullpath: Path):
        if not fullpath.is_dir():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a directory"))
        self.fullpath = fullpath  # Path relative to Project's root DIR
        self.files = []
        self.dirs = []

    @property
    def name(self) -> str:
        return self.fullpath.name
