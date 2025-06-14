import argparse
import os
from dataclasses import dataclass
from pathlib import Path

_PROJECT_NAME = "BLACKHOLE"

_DESCRIPTION = (
    "BLACKHOLE — Collapse an entire project into a single C++ file.\n"
    "Generates a self-reconstructing source file that restores all code, assets, and structure.\n"
    "Ideal for legendary submissions, strict file count limits, or compression-based defiance."
)

_EPILOGUE = (
    "Once created, the generated blackhole.cpp file is your monolith.\n"
    "It contains everything: logic, layout, legacy.\n\n"
    "→ Compile it. Run it. Watch your project reassemble itself.\n"
    "→ Collapse responsibly."
)


@dataclass
class CliArgs:
    project_dir: Path
    output_file: str


def parse_cli_args() -> CliArgs:
    parser = argparse.ArgumentParser(
        prog=_PROJECT_NAME,
        description=_DESCRIPTION,
        epilog=_EPILOGUE,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--project-dir", required=True, type=Path, help="Full path to the project's main directory.")
    parser.add_argument("--output-file", required=True, help="Filename of resulting .cpp file")

    parsed_args = parser.parse_args()

    cli_args = CliArgs(
        project_dir=parsed_args.project_dir,
        output_file=parsed_args.output_file
    )
    _validate_cli_args(cli_args)

    return cli_args


def _validate_cli_args(cli_args: CliArgs):
    if not cli_args.project_dir.is_dir():
        raise ValueError(f"--project-dir must be a valid directory: {cli_args.project_dir}")
    if os.path.isfile(cli_args.output_file):
        raise ValueError(
            f"File {cli_args.output_file} already exists in CWD."
            f"CWD = {os.getcwd()}"
        )
