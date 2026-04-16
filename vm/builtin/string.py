from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


STRING_HEADER_SIZE = 2
_CAPACITY_OFFSET = 0
_LENGTH_OFFSET = 1
_DATA_OFFSET = 2


def _normalize_char(char_code: int) -> int:
    return char_code & 0xFFFF


def _validate_string_handle(vm: VirtualMachine, handle: int) -> tuple[int, int]:
    allocated_words = vm.memory.heap_allocations.get(handle)
    if allocated_words is None:
        raise ValueError(f"String: неизвестный дескриптор строки {handle}")

    if allocated_words < STRING_HEADER_SIZE:
        raise ValueError(f"String: поврежденный блок памяти по адресу {handle}")

    capacity = vm.memory.memory[handle + _CAPACITY_OFFSET]
    length = vm.memory.memory[handle + _LENGTH_OFFSET]

    if capacity < 0:
        raise ValueError(f"String: отрицательная емкость по адресу {handle}")
    if allocated_words < capacity + STRING_HEADER_SIZE:
        raise ValueError(f"String: недостаточный размер блока по адресу {handle}")
    if not 0 <= length <= capacity:
        raise ValueError(f"String: некорректная длина {length} (capacity={capacity})")

    return capacity, length


def vm_string_to_text(vm: VirtualMachine, handle: int) -> str:
    if handle == 0:
        return ""

    _, length = _validate_string_handle(vm, handle)
    chars = [
        chr(vm.memory.memory[handle + _DATA_OFFSET + i] & 0xFFFF) for i in range(length)
    ]
    return "".join(chars)


def vm_string_from_text(vm: VirtualMachine, text: str) -> int:
    handle = StringLibrary._allocate(vm, len(text))
    for char in text:
        StringLibrary._append_char_raw(vm, handle, ord(char))
    return handle


class StringLibrary:
    name = "String"

    @staticmethod
    def _allocate(vm: VirtualMachine, max_length: int) -> int:
        if max_length < 0:
            raise ValueError("String.new: отрицательная длина")

        handle = vm.memory.allocate_heap(max_length + STRING_HEADER_SIZE)
        vm.memory.memory[handle + _CAPACITY_OFFSET] = max_length
        vm.memory.memory[handle + _LENGTH_OFFSET] = 0
        return handle

    @staticmethod
    def _append_char_raw(vm: VirtualMachine, handle: int, char_code: int):
        capacity, length = _validate_string_handle(vm, handle)
        if length >= capacity:
            raise ValueError("String.appendChar: превышена максимальная длина")

        vm.memory.memory[handle + _DATA_OFFSET + length] = _normalize_char(char_code)
        vm.memory.memory[handle + _LENGTH_OFFSET] = length + 1

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "new": BuiltinFunction(num_args=1, implementation=self._new),
            "dispose": BuiltinFunction(num_args=1, implementation=self._dispose),
            "length": BuiltinFunction(num_args=1, implementation=self._length),
            "charAt": BuiltinFunction(num_args=2, implementation=self._char_at),
            "setChar": BuiltinFunction(num_args=3, implementation=self._set_char),
            "appendChar": BuiltinFunction(num_args=2, implementation=self._append_char),
            "eraseLastChar": BuiltinFunction(
                num_args=1,
                implementation=self._erase_last_char,
            ),
            "intValue": BuiltinFunction(num_args=1, implementation=self._int_value),
            "setInt": BuiltinFunction(num_args=2, implementation=self._set_int),
            "newLine": BuiltinFunction(num_args=0, implementation=self._new_line),
            "backSpace": BuiltinFunction(num_args=0, implementation=self._back_space),
            "doubleQuote": BuiltinFunction(
                num_args=0, implementation=self._double_quote
            ),
        }

    @staticmethod
    def _new(args: list[int], vm: VirtualMachine) -> int:
        max_length = args[0]
        return StringLibrary._allocate(vm, max_length)

    @staticmethod
    def _dispose(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        vm.memory.free_heap(handle)
        return 0

    @staticmethod
    def _length(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        _, length = _validate_string_handle(vm, handle)
        return length

    @staticmethod
    def _char_at(args: list[int], vm: VirtualMachine) -> int:
        handle, index = args
        _, length = _validate_string_handle(vm, handle)
        if not 0 <= index < length:
            raise ValueError(
                f"String.charAt: индекс вне диапазона (index={index}, length={length})"
            )
        return vm.memory.memory[handle + _DATA_OFFSET + index]

    @staticmethod
    def _set_char(args: list[int], vm: VirtualMachine) -> int:
        handle, index, char_code = args
        _, length = _validate_string_handle(vm, handle)
        if not 0 <= index < length:
            raise ValueError(
                f"String.setChar: индекс вне диапазона (index={index}, length={length})"
            )
        vm.memory.memory[handle + _DATA_OFFSET + index] = _normalize_char(char_code)
        return 0

    @staticmethod
    def _append_char(args: list[int], vm: VirtualMachine) -> int:
        handle, char_code = args
        StringLibrary._append_char_raw(vm, handle, char_code)
        return handle

    @staticmethod
    def _erase_last_char(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        _, length = _validate_string_handle(vm, handle)
        if length == 0:
            raise ValueError("String.eraseLastChar: строка уже пустая")

        vm.memory.memory[handle + _LENGTH_OFFSET] = length - 1
        vm.memory.memory[handle + _DATA_OFFSET + length - 1] = 0
        return 0

    @staticmethod
    def _int_value(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        text = vm_string_to_text(vm, handle).strip()
        if not text:
            return 0

        sign = -1 if text.startswith("-") else 1
        if text[0] in "+-":
            text = text[1:]

        value = 0
        for char in text:
            if not char.isdigit():
                break
            value = value * 10 + (ord(char) - ord("0"))
        return sign * value

    @staticmethod
    def _set_int(args: list[int], vm: VirtualMachine) -> int:
        handle, value = args
        text = str(value)
        capacity, _ = _validate_string_handle(vm, handle)
        if len(text) > capacity:
            raise ValueError("String.setInt: число не помещается в строку")

        vm.memory.memory[handle + _LENGTH_OFFSET] = 0
        for index, char in enumerate(text):
            vm.memory.memory[handle + _DATA_OFFSET + index] = _normalize_char(ord(char))
        vm.memory.memory[handle + _LENGTH_OFFSET] = len(text)

        for index in range(len(text), capacity):
            vm.memory.memory[handle + _DATA_OFFSET + index] = 0
        return 0

    @staticmethod
    def _new_line(args: list[int], vm: VirtualMachine) -> int:
        return ord("\n")

    @staticmethod
    def _back_space(args: list[int], vm: VirtualMachine) -> int:
        return ord("\b")

    @staticmethod
    def _double_quote(args: list[int], vm: VirtualMachine) -> int:
        return ord('"')
