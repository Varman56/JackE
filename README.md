# JackE

_Русская версия README [здесь](README_ru.md)._

---
This project includes a compiler and emulator for the HACK computer virtual machine from
the [NAND-TO-TETRIS](https://www.nand2tetris.org/) course.

## Initial setup

### 1. Install uv

If you don't have `uv` installed yet, install it:

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or via pip:**

```bash
pip install uv
```

### 2. Create a virtual environment and install dependencies

```bash
uv sync
```

### 3. Activate the virtual environment

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```powershell
.venv\Scripts\activate
```

## Quick start

### Install JackE as a CLI tool

From the project root:

```bash
uv pip install -e .
```

To verify the installation, get information about the flags:

```bash
jacke -h
```

After this, the `jacke` command is available from any directory in the current environment:

```bash
jacke /path/to/jack/files
```

## Compiler

More information about the compiler can be found [here](compiler/README.md)

## Virtual machine

More information about the vm can be found [here](vm/README.md)

## Development

### Pre-commit workflow

Run these commands before each commit:

```bash
# 1. Code formatting
uv run ruff format .

# 2. Fix linter issues
uv run ruff check --fix .

# 3. Type checking
uv run mypy vm/ compiler/ main.py

# 4. If everything is OK, commit
git add .
git commit -m "your commit message"

# tests will be added soon...
```

### Alternative: all in one line

```bash
ruff format . && uv run ruff check --fix . && mypy vm/ compiler/ && echo "✅ All checks passed!"
```

## Adding new dependencies

```bash
uv add package-name
```

## Troubleshooting

### Python version issues

If Python 3.14 is required, but you have a different version:

```bash
uv python install 3.14
uv python pin 3.14
```

### Reset the environment

```bash
rm -rf .venv
uv sync
```
