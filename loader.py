import os
from pathlib import Path
from models import *


def map_directory(dir_path: Path) -> Directory:
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path.resolve()}")

    def recurse(fullpath: Path):
        curr_dir = Directory(fullpath)
        for item in fullpath.iterdir():
            if item.is_dir():
                curr_dir.dirs.append(recurse(item))
                continue
            if not item.is_file():
                print(f"Unknown type of directory item (NOT FILE, NOT DIR): {item}")
                continue
            if not os.access(item, os.R_OK):
                print(f"Skipping unreadable file: {item}")
                continue
            permissions = item.stat().st_mode & 0o777  # we extract the file permissions
            curr_file = File(item, permissions)
            curr_file.data = read_file_data(item)
            curr_file.is_binary = isinstance(curr_file.data, bytes)
            if curr_file.is_loaded:
                curr_dir.files.append(curr_file)
        return curr_dir

    def read_file_data(item: Path) -> Optional[Union[str, bytes]]:
        try:
            with open(item, 'r', encoding='utf-8') as fin:
                return fin.read()
        except (UnicodeDecodeError, OSError):
            try:
                with (open(item, 'rb') as fin):
                    return fin.read()
            except OSError:
                print(f"Skipping file: {item} (Could not read neither as utf-8 nor raw_bytes)")
        return None

    return recurse(dir_path.resolve())
