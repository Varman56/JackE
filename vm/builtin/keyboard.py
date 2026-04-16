import sys
from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction
from vm.builtin.string import vm_string_from_text, vm_string_to_text

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class KeyboardLibrary:
    name = "Keyboard"

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
        # В консольной реализации нет неблокирующей проверки клавиш.
        return 0

    @staticmethod
    def _read_char(args: list[int], vm: VirtualMachine) -> int:
        value = sys.stdin.read(1)
        if value == "":
            raise ValueError("Keyboard.readChar: достигнут конец ввода")
        return ord(value[0])

    @staticmethod
    def _read_line(args: list[int], vm: VirtualMachine) -> int:
        prompt_handle = args[0]
        prompt = KeyboardLibrary._resolve_prompt(vm, prompt_handle)
        try:
            line = input(prompt)
        except EOFError:
            line = ""

        return vm_string_from_text(vm, line)

    @staticmethod
    def _read_int(args: list[int], vm: VirtualMachine) -> int:
        prompt_handle = args[0]
        prompt = KeyboardLibrary._resolve_prompt(vm, prompt_handle)
        try:
            raw_value = input(prompt)
        except EOFError as exc:
            raise ValueError("Keyboard.readInt: достигнут конец ввода") from exc

        raw_value = raw_value.strip()
        if raw_value == "":
            return 0

        try:
            return int(raw_value)
        except ValueError as exc:
            raise ValueError(
                f"Keyboard.readInt: не удалось преобразовать '{raw_value}' в int"
            ) from exc

    @staticmethod
    def _resolve_prompt(vm: VirtualMachine, handle: int) -> str:
        if handle == 0:
            return ""
        return vm_string_to_text(vm, handle)
