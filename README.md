# Project Blackhole

> Collapse an entire project into a single self-reconstructing `.cpp` file.  
> Built for overengineered rebellion, binary smuggling, and bypassing ridiculous file count limits.

> _“Everything's a file. Now your project is one too.”_

---

## Overview

**Blackhole** is a Python-powered packaging tool that transforms a whole directory — including code, assets, binaries, and structure — into a single C++17-compatible source file.  
When compiled, this file produces an executable that reconstructs the original project structure and contents with near-perfect fidelity.

No zips. No tars. Just a single pure `.cpp`.

---

## Features

- Recursive directory traversal
- Text files embedded as UTF-8 raw C++ strings
- Binary files encoded in compact ASCII85
- Reconstructs files + directory structure + permissions
- Stylized console progress banner

---

## Use Cases

Originally designed to bypass a **100-file submission limit** in a compiler class by collapsing **600+** files (including binaries) into a single `.cpp`. Works great for:

- Competitive programming shenanigans
- Self-extracting project archives
- Submissions to systems with strict file constraints
- Eternal monument builds

---

## Requirements

- Python 3.7+
- A C++17 (or higher) compatible compiler (e.g. `g++`, `clang++`)

---

## CLI Usage

```bash
python3 launch.py --project-dir <YOUR_PROJECT_PATH> --output-file <FILENAME>
```

---

## Output Structure

- Each file is a C++ `File*` object with metadata
- Directory structure is defined via `Directory*` and nested relationships
- File contents are loaded via hundreds of `loader_file_N()` functions
- Final `main()`:
    - Loads content
    - Binds directory tree
    - Reconstructs to the current working path

---

## Encoding Details

- **Text files**: embedded directly as raw strings (`R"DELIM(...)"`)
- **Binary files**: encoded via custom ASCII85 implementation
    - Collisions in raw string delimiters are actively avoided with random suffixing
    - Binary decoding happens at runtime

---

## Safety Notes

- Reconstructor **aborts** if:
    - Target directories or files already exist
- No automatic backup or overwrite prompts

---

## Scale Example
 
Successfully tested with:

- ~700MB directory
- 4,667 files
- 304 subdirectories
- Mix of source code, PDFs, images, and more

---

## Limitations

- For text files written in Windows OS, the `\r\n` line endings are replaced by `\n`
- High memory usage for large projects (everything stored in RAM)
- Compile times increase with `.cpp` size
- No incremental updates
- No encryption (but could be added)

---

## License

**Blackhole** © 2025 by Georgios Evangelinos  
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — You must distribute your contributions under the same license.

[Read the full license](https://creativecommons.org/licenses/by-nc-sa/4.0/)

> TL;DR: Use it, remix it, pass it on — just don’t sell it.

---

## Author

**Georgios Evangelinos**  
Originally written to defy limits in a compiler course.  
Hack the system — collapse responsibly.