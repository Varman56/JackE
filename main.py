import argparse
from pathlib import Path

from compiler.compiler import Compiler
from vm.core.runtime import VirtualMachine
from vm.run import parse_vm_input

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GRAMMAR_FILE = BASE_DIR / "compiler" / "grammar" / "grammar.slr"
DEFAULT_STATES_FILE = BASE_DIR / "compiler" / "grammar" / "jack_slr_table.csv"


def _run_vm_program(vm_path: Path, debug: bool, show_stack: bool) -> int:
    try:
        print(f"Загрузка программы: {vm_path}")
        program = parse_vm_input(vm_path)
        print(f"Загружено инструкций: {len(program.instructions)}")
        print()

        if debug:
            print("=" * 60)
            print("Режим отладки")
            print("=" * 60)
            print()

        vm = VirtualMachine(debug=debug)
        vm.run_program(program)

        print()
        print("=" * 60)
        print("Выполнение завершено")
        print("=" * 60)

        if show_stack:
            print(f"Стек: {vm.get_stack()}")

        if vm.get_stack():
            print(f"Верхнее значение стека: {vm.get_stack_top()}")
        else:
            print("Стек пуст")

        return 0

    except KeyboardInterrupt:
        vm.screen.close_screen()
        print()
        print("=" * 60)
        print("Выполнение программы было прервано пользователем")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"Ошибка: {e}")
        if debug:
            import traceback

            traceback.print_exc()
        return 1


def main():
    arg_parser = argparse.ArgumentParser(
        description="Компиляция Jack в VM и запуск в виртуальной машине"
    )
    args_def = [
        (("path",), dict(help="Путь к .jack файлу или папке")),
        (
            ("-o", "--out-path"),
            dict(default="./build", help="Папка для .vm (по умолчанию ./build)"),
        ),
        (
            ("-g", "--grammar-file"),
            dict(
                default=str(DEFAULT_GRAMMAR_FILE),
                help="Путь до файла грамматики jack",
            ),
        ),
        (
            ("-s", "--states-file"),
            dict(
                default=str(DEFAULT_STATES_FILE),
                help="Путь до slr таблицы",
            ),
        ),
        (
            ("--build-grammar",),
            dict(action="store_true", help="Пересобрать SLR-таблицу"),
        ),
        (
            ("--ignore-build-exist",),
            dict(
                action="store_true",
                help="Игнорировать предупреждение о перезаписи и удалении файлов",
            ),
        ),
        (
            ("--show-resolved-funcs",),
            dict(
                action="store_true",
                help="Вывод информации об обнаруженных функциях",
            ),
        ),
        (
            ("--no-run",),
            dict(
                action="store_true",
                help="Только компиляция без запуска VM",
            ),
        ),
        (
            ("-d", "--debug"),
            dict(
                action="store_true",
                help="Режим отладки VM (показывает выполнение каждой инструкции)",
            ),
        ),
        (
            ("--show-stack",),
            dict(
                action="store_true",
                help="Показать содержимое стека после выполнения",
            ),
        ),
    ]
    for flags, kwargs in args_def:
        arg_parser.add_argument(*flags, **kwargs)

    args = arg_parser.parse_args()

    c = Compiler(
        path=args.path,
        out_path=args.out_path,
        grammar_file=args.grammar_file,
        states_file=args.states_file,
        build_grammar=args.build_grammar,
        ignore_build_exist=args.ignore_build_exist,
        show_resolved_funcs=args.show_resolved_funcs,
    )
    input_files = c.get_files()
    if not input_files:
        print("Ошибка: .jack файлы не найдены по указанному пути")
        return 1

    success_files = c.compile()
    if len(success_files) != len(input_files):
        print("Компиляция завершилась с ошибками. Запуск VM отменен.")
        return 1

    if args.no_run:
        return 0

    return _run_vm_program(Path(args.out_path), args.debug, args.show_stack)


if __name__ == "__main__":
    raise SystemExit(main())
