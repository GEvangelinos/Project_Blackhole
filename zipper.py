from typing import TextIO
from models import Directory


def open_output_file(output_file_name: str) -> TextIO:
    return open(f"{output_file_name}.cpp", 'w')


def close_output_file(fout: TextIO) -> None:
    fout.close()


def generate_supernova(root_dir: Directory, fout: TextIO):
    generate_prologue(root_dir, fout)



def generate_prologue(fout: TextIO) -> None:
    fout.write("""\
#include <string>
#include <vector>

class File
{
public:

private:
    // Note: we use `const char *` to save each line, as each line exists in this very file...
    std::vector<const char *> lines; 
};

class Directory
{
public:

private:
    std::vector<File> files;
    std::vector<Directory> dirs;
};
"""
               )


# Don't put everything inside main... Instead, put them as global objects: Fil1, file2, file3 and so on...
# or inside DIR vector (each dir has files). But DIRS should be a single DIR and recursively build it.
# Root to leafs (top to bottom).
def generate_main(root_dir: Directory, fout: TextIO) -> None:
    fout.write("""\
void main()
{
}
"""
               )
