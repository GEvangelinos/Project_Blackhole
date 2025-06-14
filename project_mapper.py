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
                curr_dir.files.append(File(item))
            else:
                print(f"Unknown type of directory item (NOT FILE, NOT DIR): {item}")
        return curr_dir

    return recurse(dir_path.resolve())


def dir_printer(dir: Directory, depth: int = 0) -> None:
    space_tab = 4 * ' '
    indentation = depth * space_tab
    print(f"{indentation}{'┣' if depth else ''}━{dir.name}")
    indentation += space_tab
    for file in dir.files:
        print(f"{indentation}┣━{file.name}")
    for child_dir in dir.dirs:
        dir_printer(child_dir, depth=depth + 1)
