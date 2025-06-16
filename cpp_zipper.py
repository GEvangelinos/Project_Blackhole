import random
from typing import TextIO
from models import *
from banner import BLACKHOLE_COMMENT_BANNER_WITH_WARNING

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
    while True:
        suffix = format(random.getrandbits(32), 'x')
        result = f"D_{suffix}"
        if curr_file.is_binary or result not in curr_file.data:
            return result


def open_output_file(output_file_name: str) -> TextIO:
    return open(f"{output_file_name}.cpp", 'w')


def close_output_file(fout: TextIO) -> None:
    fout.close()


def generate_all(root_dir: Directory, fout: TextIO):
    fout.write(generate_prologue())
    fout.write(generate_directory_creation_code(root_dir))
    fout.write(generate_file_creation_code(root_dir))
    fout.write(generate_directory_binding_code(root_dir))
    fout.write(generate_file_binding_code(root_dir))
    fout.write(generate_all_declarations(root_dir))
    fout.write(generate_main(root_dir))
    fout.write(generate_cpp_reconstructor())
    fout.write(generate_all_loader_definition_code(root_dir))


def generate_prologue() -> str:
    return (f"""\
{BLACKHOLE_COMMENT_BANNER_WITH_WARNING}

#include <cstdlib>
#include <format>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
 
std::filesystem::perms int_to_perms(int mode)
{{
        using perms = std::filesystem::perms;
        
        mode &= static_cast<int>(perms::mask); // Masking to keep only valid permissions.
        return static_cast<perms>(mode);
}}


class File
{{
public:
    const char *const name;
    const int perm_mode;
    const bool is_binary;
    
    explicit File(const char *name, const int perm_mode, const bool is_binary) noexcept
        : name(name), perm_mode(perm_mode), is_binary(is_binary){{}}
        
    void attach_data(const char *const data)
    {{
        if (!data_) [[likely]]
        {{
            data_ = data;
            return;
        }}
        std::cerr << __FILE__ << ':' << __LINE__ << " -> " << __func__ << "(): "
                  << "Blackhole has a logic error. Tried reassigning `data_` on file: " << this->name
                  << std::endl;
        std::abort();
    }}
    
    const char *data() const
    {{
        if (data_) [[likely]]
            return data_;
        std::cerr << __FILE__ << ':' << __LINE__ << " -> " << __func__ << "(): "
                  << "Blackhole has a logic error. Tried retrieving `data_` on file: " << this->name
                  << " --  but found nullptr"
                  << std::endl;
        std::abort();
    }}
    
private:
    const char *data_ = nullptr;
}};

class Directory
{{
public:
    const char *const name;
    
    explicit Directory(const char *name) noexcept
        : name(name) {{}}
    
    void add_subdir(const Directory *const subdir) 
    {{
        dirs_.push_back(subdir);
    }}
    
    void add_file(const File *const file)
    {{
        files_.push_back(file);
    }}
    
    const auto &files() const noexcept {{ return files_; }}
    const auto &dirs() const noexcept {{ return dirs_; }}

private:
    std::vector<const File *> files_;
    std::vector<const Directory *> dirs_;
}};
""")


def generate_directory_creation_code(root_dir: Directory) -> str:
    first_generated_dir_id = None

    def gen_code_dirs(parent_dir: Directory) -> List[str]:
        nonlocal first_generated_dir_id
        code_lines: List[str] = []

        parent_dir.mapped_code_id = gen_dir_id()

        # Capture the ID of the first generated directory (i.e., the root)
        if first_generated_dir_id is None:
            first_generated_dir_id = parent_dir.mapped_code_id

        code_lines.append(f'Directory *const {parent_dir.mapped_code_id} = new Directory("{parent_dir.name}");\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gen_code_dirs(child_dir))
        return code_lines

    code_body = ''.join(gen_code_dirs(root_dir))
    code_body += f'const Directory *const {ROOT_CODE_DIR} = {first_generated_dir_id};\n'
    return code_body


def generate_file_creation_code(root_dir: Directory) -> str:
    def gen_code_files(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            file.mapped_code_id = gen_file_id()
            code_lines.append(
                f'File *const {file.mapped_code_id} = new File("{file.name}", {file.permissions}, {str(file.is_binary).lower()});\n')
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


def generate_all_declarations(root_dir: Directory) -> str:
    declaration_code_parts: List[str] = []
    declaration_code_parts.append(generate_all_file_loader_declarations(root_dir))
    declaration_code_parts.append(f"{CppFunctionSignatures.RECONSTRUCTOR};\n")
    return ''.join(declaration_code_parts)


def generate_all_file_loader_declarations(root_dir: Directory) -> str:
    def gather_loader_declarations(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            if not file.is_loaded:  # We don't load file that can not be represented in UTF-8 (like binary files)
                continue
            code_lines.append(f'void {LOADER_FUNC_PREFIX}{file.mapped_code_id}();\n')
        for child_dir in parent_dir.dirs:
            code_lines.extend(gather_loader_declarations(child_dir))
        return code_lines

    return ''.join(line for line in gather_loader_declarations(root_dir))


def generate_main(root_dir: Directory) -> str:
    return (f"""
int main()
{{
    // Reminded that dir_0  is always the root of the whole project...
{generate_loader_calls(root_dir)}
    {DIR_BINDER_FUNCNAME}();
    {FILE_BINDER_FUNCNAME}();
    
    reconstructor({ROOT_CODE_DIR}, std::filesystem::current_path());
}}
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


def generate_cpp_reconstructor() -> str:
    # Reconstructor singature:
    # void reconstructor(const Directory *const root_dir, const std::filesystem::path basepath)
    return (f"""\
{CppFunctionSignatures.RECONSTRUCTOR}
{{
    namespace fs = std::filesystem;
    const fs::path curr_dirpath = basepath / root_dir->name;
    if (fs::exists(curr_dirpath))
    {{
        std::cerr << "Reconstruction error: In path "  << curr_dirpath.string()
                  << " -- "
                  << "directory: " << root_dir->name <<  " already exists"
                  << std::endl;
        return;
    }}
    fs::create_directory(curr_dirpath);
    for (const File *const file : root_dir->files())
    {{
        fs::path filepath = curr_dirpath / file->name;
        if (fs::exists(filepath))
        {{
            std::cerr << "Reconstruction error: In path " << curr_dirpath.string()
                      << " -- "
                      << "file: " << file->name  << " already exists"
                      << std::endl;
            continue;
        }}
        if (file->is_binary)
        {{
            std::ofstream fout(filepath, std::ios::binary);
            fout << file->data();
        }}
        else
        {{
            std::ofstream fout(filepath);
            fout << file->data();
        }}
        std::filesystem::permissions(filepath, int_to_perms(file->perm_mode), fs::perm_options::replace);
    }}
    
    for (const Directory *const child_dir : root_dir->dirs())
    {{
        reconstructor(child_dir, curr_dirpath);
    }}
}}
""")


def generate_all_loader_definition_code(root_dir: Directory) -> str:
    def emit_file_content_for_dir(parent_dir: Directory) -> List[str]:
        code_lines: List[str] = []
        for file in parent_dir.files:
            if not file.is_loaded:  # We don't load file that can not be represented in UTF-8 (like binary files)
                continue
            delim = gen_rstr_delimiter(file)  # Each file gets its own.
            code_lines.append(
                f'void {LOADER_FUNC_PREFIX}{file.mapped_code_id}()\n'
                f'{{\n'
                f'\t{file.mapped_code_id}->attach_data(\n'
                f'R"{delim}({f"{''.join(f'{b:02x}' for b in file.data)}" if file.is_binary else file.data}){delim}");\n'
                f'}}\n'
            )
            # x = fin.read()
            # for byte in x:
            #     print(f"{byte:b}", end='')
        for child_dir in parent_dir.dirs:
            code_lines.extend(emit_file_content_for_dir(child_dir))
        return code_lines

    return ''.join(line for line in emit_file_content_for_dir(root_dir))
