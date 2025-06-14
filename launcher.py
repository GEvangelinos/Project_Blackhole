import zipper
from cli_parser import *
from project_mapper import map_directory, dir_printer


def main():
    cli_args = parse_cli_args()
    root_dir = map_directory(cli_args.project_dir)
    fout = zipper.open_output_file(cli_args.output_file)
    zipper.generate_supernova(root_dir, fout)
    zipper.close_output_file(fout)


if __name__ == "__main__":
    main()
