from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from debug_tools import attach_context


class File:
    def __init__(self, fullpath: Path):
        self._text: Optional[str] = None
        self._mapped_code_id: Optional[str] = None

        if not fullpath.is_file():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a file"))
        self.fullpath = fullpath  # Path relative to Project's root DIR

    @property
    def name(self) -> str:
        return self.fullpath.name

    @property
    def text(self) -> str:
        assert self._text is not None, f"Attempted to access `.text` before it was loaded for file: {self.fullpath}"
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        assert self._text is None, f"Attempted to set `.text` twice for file: {self.fullpath}"
        self._text = value

    @property
    def is_loaded(self) -> bool:
        return self._text is not None

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
ROOT_CODE_DIR = "ROOT_DIR"
DIR_BINDER_FUNCNAME = "bind_directories"
FILE_BINDER_FUNCNAME = "bind_files_to_dirs"


@dataclass(frozen=True)
class CppFunctionSignatures:
    DIR_BINDER = f"void {DIR_BINDER_FUNCNAME}()"
    FILE_BINDER = f"void {FILE_BINDER_FUNCNAME}()"
    FILE_LOADER = "void inject_file_contents()"
    RECONSTRUCTOR = "void reconstructor(const Directory *const root_dir, const std::filesystem::path basepath)"
