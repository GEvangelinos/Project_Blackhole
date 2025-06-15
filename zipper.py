import random
from typing import TextIO, List
from models import Directory, File, CppFunctionSignatures, LOADER_FUNC_PREFIX

_file_count: int = 0
_dir_count: int = 0


def gen_file_id() -> str:
    global _file_count
    result = f"file_{_file_count}"
    _file_count += 1
    return result


def gen_dir_id() -> str:
    global _dir_count
    result = f"dir_{_dir_count}"
    _dir_count += 1
    return result


def gen_rstr_delimiter(curr_file: File) -> str:
    file_text = '\n'.join(line for line in curr_file.lines)
    while True:
        suffix = format(random.getrandbits(32), 'x')
        result = f"D_{suffix}"
        if result not in file_text:
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
    fout.write(generate_prologue())
    fout.write(generate_directory_creation_code(root_dir))
    fout.write(generate_file_creation_code(root_dir))
    fout.write(generate_directory_binding_code(root_dir))
    fout.write(generate_file_binding_code(root_dir))
    fout.write(generate_all_file_loader_declarations(root_dir))
    fout.write(generate_main(root_dir))
    fout.write(generate_cpp_reconstructor(root_dir))
    fout.write(generate_all_loader_definition_code(root_dir))


def generate_prologue() -> str:
    return ("""\
#include <cstdlib>
#include <format>
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>

class File
{
public:
    const char *const name;
    
    explicit File(const char *name) noexcept
        : name(name) {}
        
    void add_text(const char *const text)
    {
        if (!text_) [[likely]]
        {
            text_ = text;
            return;
        }
        std::cerr << std::format(
                    "{}:{} -> {}() Blackhole has a logic error. Tried reassigning `text` on file: {} ",
                     __FILE__, __LINE__,  __func__, name) 
                  << std::endl;
        std::abort();
    }
    
private:
    const char *text_ = nullptr;
};

class Directory
{
public:
    const char *const name;
    
    explicit Directory(const char *name) noexcept
        : name(name) {}
    
    void add_subdir(const Directory *const subdir) 
    {
        dirs_.push_back(subdir);
    }
    
    void add_file(const File *const file)
    {
        files_.push_back(file);
    }
    
    const auto &files() const noexcept { return files_; }
    const auto &dirs() const noexcept { return dirs_; }

private:
    
    std::vector<const File*> files_;
    std::vector<const Directory*> dirs_;
};
""")


def generate_loader_calls(root_dir: Directory) -> str:
    def recurse(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            code_lines.append(f'\t{LOADER_FUNC_PREFIX}{file.mapped_code_id}();\n')  # generate loader calls
        for child_dir in parent_dir.dirs:
            code_lines.extend(recurse(child_dir))
        return code_lines

    return ''.join(recurse(root_dir))


def generate_main(root_dir: Directory) -> str:
    return (
        f'int main()\n'
        f'{{\n'
        f'{generate_loader_calls(root_dir)}'
        f'\t// Reminded that dir_0  is always the root of the whole project...\n'
        f'}}\n'
    )


def generate_cpp_reconstructor(root_dir: Directory) -> str:
    return (
        f'void reconstuctor(const Directory *const root_dir)\n'
        f'{{\n'
        f'\tnamespace fs = std::filesystem;\n'
        f'\tfs::create_directory(root_dir->name);\n'
        f'\tfs::current_path(root_dir->name);\n'
        f'\tfor(const File* const file: root_dir->files())\n'
        f'}}\n'
    )


def generate_directory_creation_code(root_dir: Directory) -> str:
    def gen_code_dirs(parent_dir: Directory) -> List[str]:
        parent_dir.mapped_code_id = gen_dir_id()
        code_lines: List[str] = []
        code_lines.append(f'Directory *const {parent_dir.mapped_code_id} = new Directory("{parent_dir.name}");\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gen_code_dirs(child_dir))
        return code_lines

    return ''.join(gen_code_dirs(root_dir))


def generate_file_creation_code(root_dir: Directory) -> str:
    def gen_code_files(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            file.mapped_code_id = gen_file_id()
            code_lines.append(f'File *const {file.mapped_code_id} = new File("{file.name}");\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gen_code_files(child_dir))
        return code_lines

    return ''.join(gen_code_files(root_dir))


def generate_directory_binding_code(root_dir: Directory) -> str:
    def gen_bind_lines(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for child_dir in parent_dir.dirs:
            code_lines.extend(gen_bind_lines(child_dir))
            code_lines.append(f'{parent_dir.mapped_code_id}->add_subdir({child_dir.mapped_code_id});\n')
        return code_lines

    indented_lines = ['\t' + line for line in gen_bind_lines(root_dir)]

    return (
        f"{CppFunctionSignatures.DIR_BINDER}\n"
        f"{{\n"
        f"{''.join(indented_lines)}"
        f"}}\n"
    )


def generate_file_binding_code(root_dir: Directory) -> str:
    def gen_bind_lines(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            code_lines.append(f'{parent_dir.mapped_code_id}->add_file({file.mapped_code_id});\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gen_bind_lines(child_dir))
        return code_lines

    indented_lines = ['\t' + line for line in gen_bind_lines(root_dir)]

    return (
        f"{CppFunctionSignatures.FILE_BINDER}\n"
        f"{{\n"
        f"{''.join(indented_lines)}"
        f"}}\n"
    )


def generate_all_file_loader_declarations(root_dir: Directory) -> str:
    def gather_loader_declarations(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            code_lines.append(f'void {LOADER_FUNC_PREFIX}{file.mapped_code_id}();\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gather_loader_declarations(child_dir))
        return code_lines

    return ''.join(line for line in gather_loader_declarations(root_dir))


def generate_all_loader_definition_code(root_dir: Directory) -> str:
    def emit_file_content_for_dir(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            delim = gen_rstr_delimiter(file)  # Each file gets its own.
            code_lines.append(
                f'void {LOADER_FUNC_PREFIX}{file.mapped_code_id}()\n'
                f'{{\n'
                f'{file.mapped_code_id}->add_text(R"{delim}({file.text}){delim}");\n'
                f'}}\n'
            )
        for child_dir in parent_dir.dirs:
            code_lines.extend(emit_file_content_for_dir(child_dir))
        return code_lines

    return ''.join(line for line in emit_file_content_for_dir(root_dir))

# Don't put everything inside main... Instead, put them as global objects: Fil1, file2, file3 and so on...
# or inside DIR vector (each dir has files). But DIRS should be a single DIR and recursively build it.
# Root to leafs (top to bottom).
# def generate_content(root_dir: Directory, fout: TextIO) -> None:
#     fout.write(
#         f'Directory *blackhole() // We return by value (utilizing copy elision)\n'
#         f'{{\n'
#     )
#
#     def recurse(root_dir: Directory) -> str:
#         root_dir.mapped_code_id = gen_dir_id()
#         fout.write(f'Directory * const {root_dir.mapped_code_id} = new Directory("{root_dir.name}");\n')
#         for child_dir in root_dir.dirs:
#             child_dir_id = recurse(child_dir)
#             fout.write(f'{root_dir.mapped_code_id}->add_subdir({child_dir_id});\n')
#
#         for file in root_dir.files:
#             file_id = gen_file_id()
#             delim = gen_rstr_delimiter(file)  # Each file gets its own.
#             fout.write(f'File *const {file_id} = new File("{file.name}");\n')
#             # f'R"{delim}(\n'
#             # f'{file.text}\n'
#             # f'){delim}");\n')
#             fout.write(f'{dir_id}->add_file({file_id});\n')
#
#         return dir_id
#
#     recurse(root_dir)
#
#     fout.write(f'}}\n')
#
#
