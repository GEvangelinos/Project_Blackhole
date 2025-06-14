import random
from typing import TextIO, List
from models import Directory, File

_delimiters_count: int = 0


def get_delimiter() -> str:
    global _delimiters_count
    result = f"CPP{_delimiters_count}"
    _delimiters_count += 1
    return result


def open_output_file(output_file_name: str) -> TextIO:
    return open(f"{output_file_name}.cpp", 'w')


def close_output_file(fout: TextIO) -> None:
    fout.close()


# Returns the filename + a random suffix hex-number (guaranteed not to exist in file)
def generate_raw_string_identifier(file: File) -> str:
    filename = file.name
    filename = filename.replace('.', "_DOT_")
    file_text = '\n'.join(file.lines)
    while True:
        suffix = format(random.getrandbits(32), 'x')
        delimiter = f"{filename}_{suffix}"
        if delimiter not in file_text:
            return delimiter


def generate_all(root_dir: Directory, fout: TextIO):
    generate_prologue(fout)
    generate_content(root_dir, fout)


def generate_prologue(fout: TextIO) -> None:
    fout.write("""\
#include <string>
#include <vector>

class File
{
public:
    const char *const name;
    
    explicit File(const char *name) noexcept
        : name(name) {}
        
    void add_line(const char *const line)
    {
        lines.push_back(line);
    }
    
private:
    // Note: we use `const char *` to save each line, as each line exists in this very file...
    std::vector<const char *> lines; 
};

class Directory
{
public:
    const char *const name;
    
    explicit Directory(const char *name) noexcept
        : name(name) {}
    
    void add_subdir(Directory &&dir) 
    {
        dirs.push_back(std::move(dir));
    }
    
    void add_file(File &&file)
    {
        files.push_back(std::move(file));
    }

private:
    
    std::vector<File> files;
    std::vector<Directory> dirs;
};
""")


# Don't put everything inside main... Instead, put them as global objects: Fil1, file2, file3 and so on...
# or inside DIR vector (each dir has files). But DIRS should be a single DIR and recursively build it.
# Root to leafs (top to bottom).
def generate_content(root_dir: Directory, fout: TextIO) -> None:
    fout.write(
        f'Directory *blackhole() // We return by value (utilizing copy elision)\n'
        f'{{\n'
        f'Directory * const root_dir = new Directory("{root_dir.name}");\n'
    )

    def recurse(root_dir: Directory) -> None:
        for file in root_dir.files:
            file_var_name = generate_raw_string_identifier(file)
            delim = get_delimiter()
            fout.write(f'File {file_var_name}("{file.name}");\n')
            for line in file.lines:
                fout.write(f'{file_var_name}.add_line(R"{delim}("{line}"){delim}");\n')

        for child_dir in root_dir.dirs:
            recurse(child_dir)
            fout.write(f'root_dir->add_subdir("{child_dir.name}");\n')

    recurse(root_dir)

    fout.write(f'}}\n')
