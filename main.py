from compiler.source.compiler import Compiler
from vm.core.runtime import VirtualMachine
from vm.core.program import Program
import argparse


def main():
    arg_parser = argparse.ArgumentParser(description="Компилятор языка Jack в VM-код")
    args_def = [
        (("path",), dict(help="Путь к .jack файлу или папке")),
        (
            ("-o", "--out-path"),
            dict(default="./build", help="Папка для .vm (по умолчанию ./build)"),
        ),
        (
            ("-g", "--grammar-file"),
            dict(
                default="./compiler/source/grammar/grammar.slr",
                help="Путь до файла грамматики jack",
            ),
        ),
        (
            ("-s", "--states-file"),
            dict(
                default="./compiler/source/grammar/jack_slr_table.csv",
                help="Путь до slr таблицы",
            ),
        ),
        (
            ("--build-grammar",),
            dict(action="store_false", help="Пересобрать SLR-таблицу"),
        ),
        (
            ("--ignore-build-exist",),
            dict(
                action="store_false",
                help="Игнорировать предупреждение о перезаписи и удалении файлов",
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
    )
    success_files = c.compile()

    vm = VirtualMachine()
    program = Program([])
    vm.run_program(program)


if __name__ == "__main__":
    main()
