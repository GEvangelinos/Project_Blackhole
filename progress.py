from enum import IntEnum, auto
import math
import banner
from debug_tools import attach_context


class Progress:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Progress, cls).__new__(cls)
        return cls._instance

    class Stage(IntEnum):
        COUNT_FILES = auto()
        LOAD_DIR_MODEL = auto()
        EXPORT_SUPPORT_SYSTEM = auto()
        EXPORT_DIRECTORY_SKELETON = auto()
        EXPORT_BINDING_CODE = auto()
        EXPORT_FILE_CONTENT = auto()
        COMPLETED = auto()

    stage_list = list(Stage)

    main_progress_ratios = {
        Stage.COUNT_FILES: 5,
        Stage.LOAD_DIR_MODEL: 40,
        Stage.EXPORT_SUPPORT_SYSTEM: 5,
        Stage.EXPORT_DIRECTORY_SKELETON: 5,
        Stage.EXPORT_BINDING_CODE: 5,
        Stage.EXPORT_FILE_CONTENT: 40,
        Stage.COMPLETED: 0  # Just a dummy marker
    }

    assert sum(main_progress_ratios.values()) == 100, "Main progress ratios do not add up to 100%"

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._stage_progress: int = 0
        self._stage = None
        self._banner_grid = Progress._init_banner_grid()
        self._banner_row_count = len(self._banner_grid)
        self._banner_column_count = len(self._banner_grid[0])
        self._initialized = True

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value: Stage):
        assert value is not None
        self._stage = value
        self._reset_stage_process()
        self._show_progress_banner()

    def _advance_stage(self):
        raise RuntimeError("Developer has  not figured out yet.. when and how to use this function. Shouldn't be used!")

        # if self.stage is None:
        #     self._stage = Progress.stage_list[0]
        #     return
        #
        # idx = Progress.stage_list.index(self.stage)
        # if idx + 1 >= len(Progress.stage_list):
        #     raise IndexError(attach_context("Already at final Progress.Stage"))
        # if self.stage not in Progress.Stage:
        #     raise ValueError(attach_context("Current stage not found in Stages"))
        # self._stage = Progress.stage_list[idx + 1]

    @property
    def stage_progress(self):
        return self._stage_progress

    @stage_progress.setter
    def stage_progress(self, value: float):
        if value < self._stage_progress:
            raise ValueError(attach_context(
                f"Cannot decrease stage progress (current: {self._stage_progress}, given: {value})"))
        self._stage_progress = value
        self._show_progress_banner()

    def _reset_stage_process(self):
        self._stage_progress = 0

    @property
    def _total_progress(self):
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
    def _init_banner_grid():
        return [[ch for ch in line] for line in banner.PROGRESS_BANNER.splitlines()]

    def _show_progress_banner(self):
        def clear_banner():
            print(f"\033[{self._banner_row_count}F", end="")

        # We print a banner box (basically a set of newlines), so clear_banner(), we won't delete previous prints.
        def print_banner_box():
            print("\n" * self._banner_row_count, end="")

        cols_to_show: int = math.ceil(self._banner_column_count * (self._total_progress / 100))

        # We print a set of newlines so that clear_banner() won't delete previous prints.
        print_banner_box()
        clear_banner()
        for row in range(self._banner_row_count):
            row_line = ""
            for col in range(cols_to_show):
                row_line += self._banner_grid[row][col]
            print(row_line)

        if self.stage != Progress.Stage.COMPLETED:
            clear_banner()


progress = Progress()
