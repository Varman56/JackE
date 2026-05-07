import sys
from threading import Lock
from typing import TYPE_CHECKING

from pynput import keyboard

from vm.builtin.registry import BuiltinFunction
from vm.builtin.string import vm_string_from_text, vm_string_to_text

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine

_KEY_TO_CODE = {
    "-": 45,
    "=": 61,
    "[": 91,
    "]": 93,
    ";": 59,
    "'": 39,
    "\\": 92,
    ",": 44,
    ".": 46,
    "/": 47,

    "enter": 128,
    "backspace": 129,

    "left": 130,
    "up": 131,
    "right": 132,
    "down": 133,

    "home": 134,
    "end": 135,
    "page_up": 136,
    "page_down": 137,
    "insert" : 138,
    "delete" : 139,
    "esc" : 140,

    "f1": 141,
    "f2": 142,
    "f3": 143,
    "f4": 144,
    "f5": 145,
    "f6": 146,
    "f7": 147,
    "f8": 148,
    "f9": 149,
    "f10": 150,
    "f11": 151,
    "f12": 152,
}


def _get_key_code(key: keyboard.KeyCode | keyboard.Key) -> int:
    if isinstance(key, keyboard.KeyCode) and key.vk and key.vk < 152:
        return key.vk
    if isinstance(key, keyboard.KeyCode):
        return _KEY_TO_CODE.get(key.char, 0)
    if isinstance(key, keyboard.Key):
        return _KEY_TO_CODE.get(key.name, 0)
    return 0
    

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
        listener = keyboard.Listener(
            on_press=KeyboardLibrary._on_press,
            on_release=KeyboardLibrary._on_release
        )
        listener.daemon = True
        listener.start()
        return 0

    @staticmethod
    def _key_pressed(args: list[int], vm: VirtualMachine) -> int:
        with KeyboardLibrary._lock:
            return KeyboardLibrary._current_key

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
    
    @staticmethod
    def _on_press(key: keyboard.KeyCode | keyboard.Key) -> None:
        code = _get_key_code(key)
        with KeyboardLibrary._lock:
            KeyboardLibrary._current_key = code
    
    @staticmethod
    def _on_release(key: keyboard.KeyCode | keyboard.Key) -> None:
        code = _get_key_code(key)
        with KeyboardLibrary._lock:
            if KeyboardLibrary._current_key == code:
                KeyboardLibrary._current_key = 0
