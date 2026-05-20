"""
Jack Compiler
Компилятор кода Jack из курса Nand to Tetris
"""

from pathlib import Path

from compiler.source.parser.parser import Parser
from compiler.source.errors.parser_errors import ERR_PARSE_READING_FILE
from compiler.source.grammar.slr import SLRParser
from compiler.source.precompile.os_subs import OsSubroutines


class Compiler:
    def __init__(
        self,
        path,
        out_path="./build",
        grammar_file="./compiler/source/grammar/grammar.slr",
        states_file="./compiler/source/grammar/jack_slr_table.csv",
        build_grammar=False,
        print_errors=True,
        pyout=print,
        pin=input,
        ignore_build_exist=False,
    ):
        self.print_errors = print_errors
        self.path = Path(path)
        self.out_path = Path(out_path)
        self.pyout = pyout
        self.pin = pin
        self.grammar_file = grammar_file
        self.states_file = states_file
        self.ignore_build_exist = ignore_build_exist
        if build_grammar:
            self.try_build_grammar()
        self.parser = Parser(grammar_file=grammar_file, states_file=states_file)

    def try_build_grammar(self):
        self.pyout("Building grammar...")
        slr = SLRParser(filename=self.grammar_file, outfile=self.states_file)
        if self.print_errors:
            if slr.errors:
                self.pyout(
                    f"Обнаружено конфликтов: {len(slr.errors)}. Грамматика может быть не SLR(1)."
                )
            for err in slr.errors:
                self.pyout(err)
        self.pyout("Building complete!\n")

    def walkdir(self):
        files = []
        for path in self.path.rglob("*.jack"):
            files.append(path)
        return files

    def get_files(self):
        if self.path.is_dir():
            return self.walkdir()
        if self.path.is_file() and self.path.suffix == ".jack":
            return [self.path]
        return []

    @staticmethod
    def open_file(filename):
        with open(filename, encoding="utf-8", mode="r") as f:
            try:
                text = f.read()
            except Exception:
                raise ERR_PARSE_READING_FILE
        return text

    def save_vm_file(self, vm_commands, class_name):
        out_path = f"{self.out_path}\\{class_name}.vm"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vm_commands) + "\n")
        return out_path

    def prepare_build(self):
        if self.out_path.exists():
            if not self.ignore_build_exist:
                ans = self.pin(
                    "build директория уже существует. Функции могут быть переопределены неверно. Введите 'y' для подтверждения: "
                )
                if ans != "y":
                    raise KeyboardInterrupt
            # rmtree(self.out_path)
        self.out_path.mkdir(parents=True, exist_ok=True)

    def precompile(self, subroutine_table, filename):
        text = self.open_file(filename)
        return self.parser.precompile(subroutine_table, text)

    def compile(self):
        self.prepare_build()

        files = self.get_files()
        subroutine_table = {}
        self.pyout(f"Reading {len(files)} files funcs...")
        for file in files:
            self.pyout(f"\n--- Processing {file} ---")
            self.pyout(
                f"-- Functions correctly found:  {self.precompile(subroutine_table, file)} ---"
            )

        self.pyout()
        self.pyout("Resolved funcs: ", *subroutine_table.values(), sep="\n")
        self.pyout("And default libraries")
        self.pyout("-" * 50)

        subroutine_table = OsSubroutines.get_table() | subroutine_table

        self.pyout()
        self.pyout(f"Compiling {len(files)} files...")

        success_files = []

        for file in files:
            self.pyout(f"\n--- Processing: {file} ---")

            text = self.open_file(file)

            success, commands, class_name = self.parser.parse(text, subroutine_table)

            res = "FAILED"
            if success:
                res = "SUCCESS"
                success_files.append(self.save_vm_file(commands, class_name))
            self.pyout(f"--- RESULT STATUS:  {res} ---")

        return success_files
