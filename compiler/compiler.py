"""
Jack Compiler
Компилятор кода Jack из курса Nand to Tetris
"""

from pathlib import Path
from shutil import rmtree

from compiler.parser.parser import Parser
from compiler.grammar.slr import SLRParser
from compiler.precompile.os_subs import OsSubroutines
from compiler.precompile.subroutine import Subroutine


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
        path: str,
        out_path: str = "./build",
        grammar_file: str = "./compiler/grammar/grammar.slr",
        states_file: str = "./compiler/grammar/jack_slr_table.csv",
        build_grammar: bool = False,
        ignore_build_exist: bool = False,
    ) -> None:
        self.path = Path(path)
        self.out_path = Path(out_path)
        self.grammar_file = Path(grammar_file)
        self.states_file = Path(states_file)
        self.ignore_build_exist = ignore_build_exist
        if build_grammar:
            self._try_build_grammar()
        self.parser = Parser(
            grammar_file=str(self.grammar_file),
            states_file=str(self.states_file),
        )

    def _try_build_grammar(self):
        """Построение грамматики (таблицы slr анализатора)"""
        print("Building grammar...")
        slr = SLRParser(
            filename=str(self.grammar_file),
            outfile=str(self.states_file),
        )
        if slr.errors:
            print(
                f"Обнаружено конфликтов: {len(slr.errors)}. Грамматика может быть не SLR(1)."
            )
        for err in slr.errors:
            print(err)
        print("Building complete!\n")

    def _walkdir(self) -> list[Path]:
        """Рекурсивный поиск всех .jack файлов в директории"""
        files = []
        for path in self.path.rglob("*.jack"):
            files.append(path)
        return files

    def get_files(self) -> list[Path]:
        """Вернуть список файлов для компиляции"""
        if self.path.is_dir():
            return self._walkdir()
        if self.path.is_file() and self.path.suffix == ".jack":
            return [self.path]
        return []

    @staticmethod
    def _open_file(filename: Path) -> str:
        """Открыть файл и прочитать данные"""
        try:
            return filename.read_text(encoding="utf-8")
        except Exception as e:
            print("Error during read file: ", e)
            return ""

    def save_vm_file(self, vm_commands, class_name) -> str:
        """Сохранение .vm файла"""
        out_path = self.out_path / f"{class_name}.vm"
        out_path.write_text("\n".join(vm_commands) + "\n", encoding="utf-8")
        return str(out_path)

    def _prepare_build(self) -> None:
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

    def _precompile(
        self, subroutine_table: dict[str, Subroutine], filename: Path
    ) -> bool:
        """Поиск функций и методов для сохранения в таблицу"""
        text = self._open_file(filename)
        return self.parser.precompile(subroutine_table, text)

    def compile(self) -> list[str]:
        """Процесс полной компиляции всех файлов. Возвращает путь до каждого успешно скомпилированного файла"""
        self._prepare_build()

        files = self.get_files()
        subroutine_table: dict[str, Subroutine] = {}
        print(f"Reading {len(files)} files funcs...")
        for file in files:
            print(f"\n--- Processing {file} ---")
            print(
                f"-- Functions correctly found:  {self._precompile(subroutine_table, file)} ---"
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

            text = self._open_file(file)

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
            print(f"Классы с ошибками компиляции: \n{'\n'.join(failed_classes)}")
            print("\nВы можете увидеть конкретные ошибки выше")
        print("-" * 50 + "\n")
        return success_files
