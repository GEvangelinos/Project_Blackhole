import cpp_zipper
from cli_parser import *
from loader import map_directory


def main():
    cli_args = parse_cli_args()
    root_dir = map_directory(cli_args.project_dir)
    fout = cpp_zipper.open_output_file(cli_args.output_file)
    cpp_zipper.generate_all(root_dir, fout)
    cpp_zipper.close_output_file(fout)


if __name__ == "__main__":
    main()
