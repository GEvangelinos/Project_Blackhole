from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from debug_tools import attach_context


class File:
    lines: List[str]

    def __init__(self, fullpath: Path):
        self.lines = []
        self._mapped_code_id: Optional[str] = None

        if not fullpath.is_file():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a file"))
        self.fullpath = fullpath  # Path relative to Project's root DIR

    @property
    def name(self) -> str:
        return self.fullpath.name

    @property
    def text(self):
        return '\n'.join(line for line in self.lines)

    @property
    def mapped_code_id(self) -> str:
        assert self._mapped_code_id is not None
        return self._mapped_code_id

    @mapped_code_id.setter
    def mapped_code_id(self, value: str) -> None:
        assert self._mapped_code_id is None
        self._mapped_code_id = value


class Directory:
    def __init__(self, fullpath: Path):
        self.files: List['File'] = []
        self.dirs: List['Directory'] = []
        self._mapped_code_id: Optional[str] = None

        if not fullpath.is_dir():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a directory"))
        self.fullpath = fullpath  # Path relative to Project's root DIR

    @property
    def name(self) -> str:
        return self.fullpath.name

    @property
    def mapped_code_id(self) -> str:
        assert self._mapped_code_id is not None
        return self._mapped_code_id

    @mapped_code_id.setter
    def mapped_code_id(self, value: str) -> None:
        assert self._mapped_code_id is None
        self._mapped_code_id = value


LOADER_FUNC_PREFIX = "loader_"

@dataclass(frozen=True)
class CppFunctionSignatures:
    DIR_BINDER = "void bind_directories()"
    FILE_BINDER = "void bind_files_to_dirs()"
    FILE_LOADER = "void inject_file_contents()"
    RECONSTRUCTOR = "void reconstructor(const Directory *const root_dir, const std::filesystem::path basepath)"
