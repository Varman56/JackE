"""
Jack Compiler
Компилятор кода Jack из курса Nand to Tetris
"""

from pathlib import Path
from shutil import rmtree

from compiler.source.parser.parser import Parser
from compiler.source.grammar.slr import SLRParser
from compiler.source.precompile.os_subs import OsSubroutines


class Compiler:
    """
    Главный класс компилятора языка Jack

    Аргументы:
    - path: Путь до папки с .jack файлами или одному файлу (При указании папки - будет произведен поиск и компиляция всех .jack файлов)
    - out_path: Пусть сохранения .vm файлов
    - grammar_file: Путь до файла грамматики (подразумевается файл грамматики jack, при изменении требуется также изменения поддержки нетерминалов компилятора, а также пересборка таблицы анализтора(build_grammar=True))
    - states_file: Путь до slr таблицы (подразумевается файл анализатора jack, она автоматически собирается из грамматики)
    - build_grammar: Пересобрать ли таблицу slr-анализатора из grammar_file в states_file
    - ignore_build_exist: Игнорировать ли предупреждение о перезаписи и удалении всей build папки (Применяйте с осторожностью)
    """

    def __init__(
        self,
        path,
        out_path="./build",
        grammar_file="./compiler/source/grammar/grammar.slr",
        states_file="./compiler/source/grammar/jack_slr_table.csv",
        build_grammar=False,
        ignore_build_exist=False,
    ):
        self.path = Path(path)
        self.out_path = Path(out_path)
        self.grammar_file = grammar_file
        self.states_file = states_file
        self.ignore_build_exist = ignore_build_exist
        if build_grammar:
            self.try_build_grammar()
        self.parser = Parser(grammar_file=grammar_file, states_file=states_file)

    def try_build_grammar(self):
        """Построение грамматики (таблицы slr анализатора)"""
        print("Building grammar...")
        slr = SLRParser(filename=self.grammar_file, outfile=self.states_file)
        if slr.errors:
            print(
                f"Обнаружено конфликтов: {len(slr.errors)}. Грамматика может быть не SLR(1)."
            )
        for err in slr.errors:
            print(err)
        print("Building complete!\n")

    def walkdir(self):
        """Рекурсивный поиск всех .jack файлов в директории"""
        files = []
        for path in self.path.rglob("*.jack"):
            files.append(path)
        return files

    def get_files(self):
        """Вернуть список файлов для компиляции"""
        if self.path.is_dir():
            return self.walkdir()
        if self.path.is_file() and self.path.suffix == ".jack":
            return [self.path]
        return []

    def open_file(self, filename):
        """Открыть файл и прочитать данные"""
        with open(filename, encoding="utf-8", mode="r") as f:
            try:
                text = f.read()
            except Exception as e:
                print("Error during read file: ", e)
                return ""
        return text

    def save_vm_file(self, vm_commands, class_name):
        """Сохранение .vm файла"""
        out_path = f"{self.out_path}\\{class_name}.vm"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vm_commands) + "\n")
        return out_path

    def prepare_build(self):
        """Очистка директрии сохранения .vm файлов"""
        if self.out_path.exists():
            if not self.ignore_build_exist:
                ans = input(
                    "build директория уже существует. Повторяющиеся классы будут перезаписаны.\nЕсли вывод компилятора - стандартная папка ('./build') - она будет очищена.\nВведите 'y' для подтверждения: "
                )
                if ans != "y":
                    exit(0)
            if self.out_path.name == "build":
                rmtree(self.out_path)
        self.out_path.mkdir(parents=True, exist_ok=True)

    def precompile(self, subroutine_table, filename):
        """Поиск функций и методов для сохранения в таблицу"""
        text = self.open_file(filename)
        return self.parser.precompile(subroutine_table, text)

    def compile(self):
        """Процесс полной компиляции всех файлов. Возвращает путь до каждого успешно скомпилированного файла"""
        self.prepare_build()

        files = self.get_files()
        subroutine_table = {}
        print(f"Reading {len(files)} files funcs...")
        for file in files:
            print(f"\n--- Processing {file} ---")
            print(
                f"-- Functions correctly found:  {self.precompile(subroutine_table, file)} ---"
            )

        print()
        print("Resolved funcs: ", *subroutine_table.values(), sep="\n")
        print("And default libraries")
        print("-" * 50)

        subroutine_table = OsSubroutines.get_table() | subroutine_table

        print()
        print(f"Compiling {len(files)} files...")

        success_files = []
        failed_classes = []

        for file in files:
            print(f"\n--- Processing: {file} ---")

            text = self.open_file(file)

            success, commands, class_name = self.parser.parse(text, subroutine_table)

            res = "FAILED"
            if success:
                res = "SUCCESS"
                success_files.append(self.save_vm_file(commands, class_name))
            else:
                failed_classes.append(class_name)
            print(f"--- RESULT STATUS:  {res} ---")

        if failed_classes:
            print()
            print(f"Classes with failures: \n{'\n'.join(failed_classes)}")
            print(f"\nYou can see the error{'s' if len(failed_classes) > 1 else ''} above")
        return success_files
