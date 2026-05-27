from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class ScreenLibrary:
    name = "Screen"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "clearScreen": BuiltinFunction(
                num_args=0, implementation=self._clear_screen
            ),
            "setColor": BuiltinFunction(num_args=1, implementation=self._set_color),
            "setColorRGB": BuiltinFunction(
                num_args=3, implementation=self._set_color_RGB
            ),
            "setFontColor": BuiltinFunction(
                num_args=3, implementation=self._set_font_color
            ),
            "drawPixel": BuiltinFunction(num_args=2, implementation=self._draw_pixel),
            "drawLine": BuiltinFunction(num_args=4, implementation=self._draw_line),
            "drawRectangle": BuiltinFunction(
                num_args=4, implementation=self._draw_rectangle
            ),
            "drawCircle": BuiltinFunction(num_args=3, implementation=self._draw_circle),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _clear_screen(args: list[int], vm: VirtualMachine) -> int:
        vm.screen.clear_screen()
        return 0

    @staticmethod
    def _set_color(args: list[int], vm: VirtualMachine) -> int:
        is_black = args[0]
        new_color = BLACK if is_black else WHITE
        vm.screen.set_color(*new_color)
        return 0

    @staticmethod
    def _set_color_RGB(args: list[int], vm: VirtualMachine) -> int:
        r, g, b = args[0], args[1], args[2]
        vm.screen.set_color(r, g, b)
        return 0

    @staticmethod
    def _set_font_color(args: list[int], vm: VirtualMachine) -> int:
        r, g, b = args[0], args[1], args[2]
        vm.screen.set_font_color(r, g, b)
        return 0

    @staticmethod
    def _draw_pixel(args: list[int], vm: VirtualMachine) -> int:
        x, y = args[0], args[1]
        vm.screen.draw_pixel(x, y)
        return 0

    @staticmethod
    def _draw_line(args: list[int], vm: VirtualMachine) -> int:
        x1, y1, x2, y2 = args[0], args[1], args[2], args[3]
        vm.screen.draw_line(x1, y1, x2, y2)
        return 0

    @staticmethod
    def _draw_rectangle(args: list[int], vm: VirtualMachine) -> int:
        x1, y1, x2, y2 = args[0], args[1], args[2], args[3]
        vm.screen.draw_rectangle(x1, y1, x2, y2)
        return 0

    @staticmethod
    def _draw_circle(args: list[int], vm: VirtualMachine) -> int:
        x, y, r = args[0], args[1], args[2]
        vm.screen.draw_circle(x, y, r)
        return 0
