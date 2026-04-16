from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction
from vm.builtin.string import vm_string_to_text

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class OutputLibrary:
    name = "Output"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "moveCursor": BuiltinFunction(num_args=2, implementation=self._move_cursor),
            "printChar": BuiltinFunction(num_args=1, implementation=self._print_char),
            "printString": BuiltinFunction(
                num_args=1, implementation=self._print_string
            ),
            "printInt": BuiltinFunction(num_args=1, implementation=self._print_int),
            "println": BuiltinFunction(num_args=0, implementation=self._println),
            "backSpace": BuiltinFunction(num_args=0, implementation=self._back_space),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _move_cursor(args: list[int], vm: VirtualMachine) -> int:
        # Для консольного режима позиционирование курсора пока игнорируем.
        return 0

    @staticmethod
    def _print_char(args: list[int], vm: VirtualMachine) -> int:
        value = args[0] & 0xFFFF
        print(chr(value))
        return 0

    @staticmethod
    def _print_string(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        print(vm_string_to_text(vm, handle))
        return 0

    @staticmethod
    def _print_int(args: list[int], vm: VirtualMachine) -> int:
        value = args[0]
        print(str(value))
        return 0

    @staticmethod
    def _println(args: list[int], vm: VirtualMachine) -> int:
        print()
        return 0

    @staticmethod
    def _back_space(args: list[int], vm: VirtualMachine) -> int:
        print("\b", end="", flush=True)
        return 0
