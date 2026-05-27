from threading import Lock
from typing import TYPE_CHECKING

from vm.builtin.output import OutputLibrary
from vm.builtin.registry import BuiltinFunction
from vm.builtin.string import vm_string_from_text, vm_string_to_text

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class KeyboardLibrary:
    name = "Keyboard"
    _lock = Lock()
    _current_key = 0

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "keyPressed": BuiltinFunction(num_args=0, implementation=self._key_pressed),
            "readChar": BuiltinFunction(num_args=0, implementation=self._read_char),
            "readLine": BuiltinFunction(num_args=1, implementation=self._read_line),
            "readInt": BuiltinFunction(num_args=1, implementation=self._read_int),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _key_pressed(args: list[int], vm: VirtualMachine) -> int:
        return vm.screen.key_pressed()

    @staticmethod
    def _read_char(args: list[int], vm: VirtualMachine) -> int:
        OutputLibrary._print_char([0], vm)  # Отрисовка курсора
        char = 0

        while vm.screen.is_alive() and (char := KeyboardLibrary._key_pressed([], vm)) == 0:
            pass

        while vm.screen.is_alive() and (new_char := KeyboardLibrary._key_pressed([], vm)) != 0:
            char = new_char

        if char not in (128, 129):
            OutputLibrary._print_char([char], vm)

        return char

    @staticmethod
    def _read_line(args: list[int], vm: VirtualMachine) -> int:
        line = KeyboardLibrary._getline(args, vm)
        return vm_string_from_text(vm, line)

    @staticmethod
    def _read_int(args: list[int], vm: VirtualMachine) -> int:
        line = KeyboardLibrary._getline(args, vm)

        num = 0
        for ch in line:
            if not ch.isdigit():
                break
            num = num * 10 + int(ch)
        return num

    @staticmethod
    def _resolve_prompt(vm: VirtualMachine, handle: int) -> str:
        if handle == 0:
            return ""
        return vm_string_to_text(vm, handle)

    @staticmethod
    def _getline(args: list[int], vm: VirtualMachine) -> str:
        OutputLibrary._print_string(args, vm)

        line = ""
        while vm.screen.is_alive():
            char = KeyboardLibrary._read_char([], vm)
            if char == 128:  # enter
                OutputLibrary._clear_cursor(vm)
                OutputLibrary._println([], vm)
                break
            elif char == 129:  # backspace
                if line == "":
                    continue
                line = line[:-1]
                OutputLibrary._back_space([], vm)
            else:
                line += chr(char)

        return line
