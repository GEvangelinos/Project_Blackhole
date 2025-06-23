import cpp_zipper
import file_handler
from cli_parser import *
from file_handler import load_dir_model


def main():
    cli_args = parse_cli_args()
    print(f"There are {file_handler.count_readable_files(cli_args.project_dir)} readable files!")
    root_dir = load_dir_model(cli_args.project_dir)
    fout = cpp_zipper.open_output_file(cli_args.output_file)
    cpp_zipper.generate_all(root_dir, fout)
    cpp_zipper.close_output_file(fout)


if __name__ == "__main__":
    main()
