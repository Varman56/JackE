# Jack Educational Language Compiler

## Quick-start

The `Compiler` class is the main one to use.

The compiler takes one positional argument - the path to a `.jack` file or folder.

If a folder is passed as an argument, the compiler will recursively traverse all subfolders of that folder and discover
all files with the `.jack` extension.

To run:

```bash
uv run python .\main.py "Path to .jack files" --no-run
```

The compiled `.vm` files will be placed in the `./build` directory.

## Arguments

```bash
positional arguments:
  path                  Path to a .jack file or folder

options:
  -h, --help            show this help message and exit
  -o, --out-path OUT_PATH
                        Folder for .vm files (default ./build)
  -g, --grammar-file GRAMMAR_FILE
                        Path to the Jack grammar file
  -s, --states-file STATES_FILE
                        Path to the SLR table
  --build-grammar       Rebuild the SLR table
  --ignore-build-exist  Ignore the warning about overwriting and deleting files
  --show-resolved-funcs
                        Output information about discovered functions
```

## WARNING

- It is not recommended to change the grammar file without
  need and understanding of what is going on.
- Adding a non-terminal or terminal requires changes to the compiler code (`CodeGenerator`, etc.).
- The standard build directory will be completely cleared.
  For safety of other data, other directories will only overwrite new vm files. (To disable the warning, see
  `ignore-build-exist`)