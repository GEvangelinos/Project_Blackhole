import os
import binary_encoder
import debug_tools
from models import *
from progress import *


def count_readable_files(dir_path: Path) -> int:
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path.resolve()}")

    progress.stage = Progress.Stage.COUNT_FILES
    progress.stage_progress = 0

    def recursive_counter(fullpath: Path) -> int:
        files_found = 0
        for item in fullpath.iterdir():
            if item.is_dir():
                files_found += recursive_counter(item)
                continue
            if not item.is_file():
                print(f"Unknown type of directory item (NOT FILE, NOT DIR): {item}")
                continue
            if not os.access(item, os.R_OK):
                print(f"Skipping unreadable file: {item}")
                continue
            files_found += 1
        return files_found

    progress.stage_progress = 1  # Stage completed!

    return recursive_counter(dir_path)


def load_dir_model(dir_path: Path, expected_files: int) -> Directory:
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path.resolve()}")

    progress.stage = Progress.Stage.LOAD_DIR_MODEL
    progress.stage_progress = 0

    files_read = 0

    def recursive_builder(fullpath: Path):
        curr_dir = Directory(fullpath)
        for item in fullpath.iterdir():
            if item.is_dir():
                curr_dir.dirs.append(recursive_builder(item))
                continue
            if not item.is_file():
                print(f"Unknown type of directory item (NOT FILE, NOT DIR): {item}")
                continue
            if not os.access(item, os.R_OK):
                print(f"Skipping unreadable file: {item}")
                continue
            permissions = item.stat().st_mode & 0o777  # we extract the file permissions
            curr_file = File(item, permissions)
            file_data = read_file_data(item)

            if isinstance(file_data, bytes):
                curr_file.data = binary_encoder.encode_ascii85(file_data)
                curr_file.is_encoded_ascii85 = True
            elif isinstance(file_data, str):
                curr_file.data = file_data
                curr_file.is_encoded_ascii85 = False
            else:
                raise RuntimeError(debug_tools.attach_context(f"Failed to load file: {item.name}"))
            if curr_file.is_loaded:
                curr_dir.files.append(curr_file)
            progress.stage_progress = files_read / expected_files
        return curr_dir

    def read_file_data(item: Path) -> Optional[Union[str, bytes]]:
        nonlocal files_read
        files_read += 1

        try:
            with open(item, 'r', encoding='utf-8') as fin:
                return fin.read()
        except (UnicodeDecodeError, OSError):
            pass
        try:
            with open(item, 'rb') as fin:
                print(f"Warning: {item} is a binary file; it will be encoded with ascii85.")
                return fin.read()
        except OSError:
            print(f"Skipping file: {item} (Could not read as UTF-8 or binary)")

        files_read -= 1  # undo the count
        return None

    dir_model = recursive_builder(dir_path.resolve())
    progress.stage_progress = 1  # Stage completed!
    return dir_model
