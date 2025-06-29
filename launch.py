from Tools.scripts.var_access_benchmark import read_deque

import cpp_zipper
import file_handler
from cli_parser import *
from file_handler import load_dir_model
from progress import *

def main():
    cli_args = parse_cli_args()
    readable_files = file_handler.count_readable_files(cli_args.project_dir)
    root_dir = load_dir_model(cli_args.project_dir, readable_files)
    fout = cpp_zipper.open_output_file(cli_args.output_file)
    cpp_zipper.generate_all(root_dir, readable_files, fout)
    cpp_zipper.close_output_file(fout)
    progress.stage = Progress.Stage.COMPLETED



if __name__ == "__main__":
    main()
