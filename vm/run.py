#!/usr/bin/env python3
"""
Hack VM - главный файл для запуска виртуальной машины
"""

import argparse
from pathlib import Path

from vm.builtin.screen import ScreenLibrary
from vm.core.instruction import Function
from vm.core.program import Program
from vm.core.runtime import VirtualMachine
from vm.parser.vm_parser import VMParser


def _wrap_with_bootstrap(vm_parser: VMParser, instructions: list) -> Program:
    wrapped_instructions = []

    bootstrap = vm_parser.parse_lines(
        [
            "call Main.main 0",
            "goto __VM_END__",
        ],
        source_file="bootstrap",
    )
    wrapped_instructions.extend(bootstrap.instructions)
    wrapped_instructions.extend(instructions)

    end_label = vm_parser.parse_lines(["label __VM_END__"], source_file="bootstrap")
    wrapped_instructions.extend(end_label.instructions)

    return Program(wrapped_instructions)


def parse_vm_input(input_path: Path) -> Program:
    """Парсит один VM-файл или директорию с несколькими VM-файлами."""
    vm_parser = VMParser()

    if input_path.is_file():
        program = vm_parser.parse_file(str(input_path))
        has_main = any(
            isinstance(instruction, Function) and instruction.name == "Main.main"
            for instruction in program.instructions
        )
        if has_main:
            return _wrap_with_bootstrap(vm_parser, program.instructions)
        return program

    vm_files = sorted(input_path.glob("*.vm"))
    if not vm_files:
        raise ValueError(f"В директории '{input_path}' нет .vm файлов")

    instructions = []

    for vm_file in vm_files:
        program = vm_parser.parse_file(str(vm_file))
        instructions.extend(program.instructions)

    return _wrap_with_bootstrap(vm_parser, instructions)


def main():
    parser = argparse.ArgumentParser(
        description="Hack Virtual Machine - эмулятор VM из курса Nand to Tetris"
    )
    parser.add_argument("file", help="VM файл или директория с .vm файлами")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Режим отладки (показывает выполнение каждой инструкции)",
    )
    parser.add_argument(
        "-s",
        "--show-stack",
        action="store_true",
        help="Показать содержимое стека после выполнения",
    )

    args = parser.parse_args()

    # Проверяем существование файла
    if not Path(args.file).exists():
        print(f"Ошибка: файл '{args.file}' не найден")
        return 1

    try:
        # Парсим программу
        print(f"Загрузка программы: {args.file}")
        program = parse_vm_input(Path(args.file))
        print(f"Загружено инструкций: {len(program.instructions)}")
        print()

        # Создаем и запускаем VM
        if args.debug:
            print("=" * 60)
            print("Режим отладки")
            print("=" * 60)
            print()

        vm = VirtualMachine(debug=args.debug)
        vm.run_program(program)

        # Результаты
        print()
        print("=" * 60)
        print("Выполнение завершено")
        print("=" * 60)

        if args.show_stack:
            print(f"Стек: {vm.get_stack()}")

        if vm.get_stack():
            print(f"Верхнее значение стека: {vm.get_stack_top()}")
        else:
            print("Стек пуст")

        return 0

    except KeyboardInterrupt as _:
        if vm.screen.is_alive():
            vm.screen.close_screen()
        print()
        print("=" * 60)
        print("Выполнение программы было прервано пользователем")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"Ошибка: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
