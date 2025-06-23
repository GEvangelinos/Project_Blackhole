from enum import Enum, auto

import banner
from debug_tools import attach_context


class Progress:
    class Stage(Enum):
        COUNT_FILES = auto()
        LOAD_DIR_MODEL = auto()
        EXPORT_SUPPORT_SYSTEM = auto()
        EXPORT_DIRECTORY_SKELETON = auto()
        EXPORT_BINDING_CODE = auto()
        EXPORT_FILE_CONTENT = auto()

    stage_list = list(Stage)

    main_progress_ratios = {
        Stage.COUNT_FILES: 5,
        Stage.LOAD_DIR_MODEL: 10,
        Stage.EXPORT_SUPPORT_SYSTEM: 5,
        Stage.EXPORT_DIRECTORY_SKELETON: 5,
        Stage.EXPORT_BINDING_CODE: 5,
        Stage.EXPORT_FILE_CONTENT: 70
    }

    assert sum(main_progress_ratios.values()) == 100, "Main progress ratios do not add up to 100%"

    def __init__(self):
        self._stage_progress: int = 0
        self._stage = None

    @property
    def stage(self):
        return self._stage

    def advance_stage(self):
        if self.stage is None:
            self._stage = Progress.stage_list[0]
            return

        idx = Progress.stage_list.index(self.stage)
        if idx + 1 >= len(Progress.stage_list):
            raise IndexError(attach_context("Already at final Progress.Stage"))
        if self.stage not in Progress.Stage:
            raise ValueError(attach_context("Current stage not found in Stages"))
        self._stage = Progress.stage_list[idx + 1]

    @property
    def stage_progress(self):
        return self._stage_progress

    @stage_progress.setter
    def stage_progress(self, value: int):
        if value <= self._stage_progress:
            raise ValueError(attach_context(
                f"Cannot decrease stage progress (current: {self._stage_progress}, given: {value})"))
        self._stage_progress = value

    @property
    def total_progress(self):
        if self.stage is None:
            return 0

        total = 0
        for s in Progress.Stage:
            if s < self.stage:
                total += Progress.main_progress_ratios[s]
            else:
                assert (0 <= self.stage_progress <= 1), "Stage progress must be between 0 and 1."
                total += Progress.main_progress_ratios[s] * self.stage_progress
                break
        else:
            raise ValueError(attach_context(f"Stage {self.stage} not found in Progress.Stage"))
        return total

    @staticmethod
    def init_banner_grid():
        return [[ch for ch in line] for line in banner.PROGRESS_BANNER.splitlines()]


    def show_progress_banner(self):
        pass
