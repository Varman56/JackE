from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction
from vm.builtin.string import vm_string_to_text
from vm.core.font import Font

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine

WIDTH, HEIGHT = 64, 23
CHAR_WIDTH, CHAR_HEIGHT = 8, 11


class Cursor:
    def __init__(self, x: int, y: int) -> None:
        self.set_cords(x, y)

    def set_cords(self, x: int, y: int) -> None:
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            raise ValueError("Выход за пределы экрана")

        self.x = x
        self.y = y

    def get_cords(self) -> tuple[int, int]:
        return self.x, self.y

    def _normalize_cords(self):
        if self.x >= WIDTH:
            self.x = 0
            self.y += 1

        if self.x < 0:
            self.x = WIDTH - 1
            self.y -= 1

        if self.y >= HEIGHT:
            self.set_cords(0, 0)

        if self.y < 0:
            self.set_cords(WIDTH - 1, HEIGHT - 1)

    def new_line(self) -> None:
        self.x = 0
        self.y += 1
        self._normalize_cords()

    def move_right(self) -> None:
        self.x += 1
        self._normalize_cords()

    def move_left(self) -> None:
        self.x -= 1
        self._normalize_cords()


class OutputLibrary:
    name = "Output"
    font = Font()
    cursor = Cursor(0, 0)

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
        y, x = args[0], args[1]
        OutputLibrary.cursor.set_cords(x, y)
        return 0

    @staticmethod
    def _print_char(args: list[int], vm: VirtualMachine) -> int:
        value = args[0] & 0xFFFF

        # printing \n
        if value == 128:
            OutputLibrary._println([], vm)
            return 0

        x, y = OutputLibrary.cursor.get_cords()
        vm.screen.clear_rectangle(
            x * CHAR_WIDTH,
            y * CHAR_HEIGHT,
            (x + 1) * CHAR_HEIGHT - 1,
            (y + 1) * CHAR_HEIGHT - 1,
        )

        char = OutputLibrary.font.get_char(value)
        for ch_y in range(CHAR_HEIGHT):
            for ch_x in range(CHAR_WIDTH):
                if not char[ch_y][ch_x]:
                    continue
                vm.screen.draw_font_pixel(x * CHAR_WIDTH + ch_x, y * CHAR_HEIGHT + ch_y)

        if value != 0:
            OutputLibrary.cursor.move_right()
        return 0

    @staticmethod
    def _print_string(args: list[int], vm: VirtualMachine) -> int:
        handle = args[0]
        text = vm_string_to_text(vm, handle)
        for ch in text:
            code = ord(ch)
            OutputLibrary._print_char([code], vm)
        return 0

    @staticmethod
    def _print_int(args: list[int], vm: VirtualMachine) -> int:
        value = args[0]
        line = str(value)
        for ch in line:
            code = ord(ch)
            OutputLibrary._print_char([code], vm)
        return 0

    @staticmethod
    def _println(args: list[int], vm: VirtualMachine) -> int:
        OutputLibrary.cursor.new_line()
        return 0

    @staticmethod
    def _back_space(args: list[int], vm: VirtualMachine) -> int:
        x, y = OutputLibrary.cursor.get_cords()

        vm.screen.clear_rectangle(
            x * CHAR_WIDTH,
            y * CHAR_HEIGHT,
            (x + 1) * CHAR_HEIGHT - 1,
            (y + 1) * CHAR_HEIGHT - 1,
        )

        OutputLibrary.cursor.move_left()
        return 0

    @staticmethod
    def _clear_cursor(vm) -> None:
        x, y = OutputLibrary.cursor.get_cords()

        vm.screen.clear_rectangle(
            x * CHAR_WIDTH,
            y * CHAR_HEIGHT,
            (x + 1) * CHAR_HEIGHT - 1,
            (y + 1) * CHAR_HEIGHT - 1,
        )
