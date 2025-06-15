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
            elif item.is_file():
                if not os.access(item, os.R_OK):
                    print(f"Skipping unreadable file: {item}")
                    continue
                try:
                    with open(item, 'rb') as fin:  # read as bytes
                        raw_bytes = fin.read()
                        file_text = raw_bytes.decode('utf-8')  # decode manually
                except UnicodeDecodeError:
                    print(f"Skipping non-text (binary or non-UTF-8) file: {item}")
                    continue

                curr_file = File(item)
                curr_file.text = file_text
                curr_dir.files.append(curr_file)
            else:
                print(f"Unknown type of directory item (NOT FILE, NOT DIR): {item}")
        return curr_dir

    return recurse(dir_path.resolve())
