from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
from debug_tools import attach_context


class File:
    def __init__(self, fullpath: Path, permissions: int):
        self._mapped_code_id: Optional[str] = None
        self._data: Optional[Union[str, bytes]] = None
        self._is_encoded_ascii85: Optional[bool] = None
        self._permissions = permissions

        if not fullpath.is_file():
            raise ValueError(attach_context(f"Fullpath: {fullpath} does not correspond to a file"))
        self.fullpath = fullpath  # Path relative to Project's root DIR

    @property
    def name(self) -> str:
        return self.fullpath.name

    @property
    def permissions(self):
        return self._permissions

    @property
    def data(self) -> str:
        assert self._data is not None, f"Attempted to access `self._data` before it was loaded for file: {self.fullpath}"
        return self._data

    @data.setter
    def data(self, value: Optional[Union[str, bytes]]) -> None:
        if value is None:
            return
        assert self._data is None, f"Attempted to set `self._data` but its already loaded. For file: {self.fullpath}"
        self._data = value

    @property
    def is_loaded(self) -> bool:
        return self._data is not None

    @property
    def is_encoded_ascii85(self) -> bool:
        assert self._is_encoded_ascii85 is not None, f"Attempted to access `self._is_encoded_ascii85` but it was never specified. For file: {self.fullpath}"
        return self._is_encoded_ascii85

    @is_encoded_ascii85.setter
    def is_encoded_ascii85(self, value: bool) -> None:
        assert self._is_encoded_ascii85 is None, f"Attempted to set `self._is_encoded_ascii85` but it already set. For file: {self.fullpath}"
        self._is_encoded_ascii85 = value

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
    DECODER = "auto decode_ascii85(const char *const encoded_data)"
