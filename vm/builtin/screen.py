from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

import pygame

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine

WIDTH, HEIGHT = 512, 256
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ICON_PATH = "JackE_icon.bmp"


class ScreenLibrary:
    name = "Screen"
    screen : pygame.Surface | None = None
    color : tuple[int, int, int] = BLACK

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "clearScreen": BuiltinFunction(num_args=0, implementation=self._clear_screen),
            "setColor": BuiltinFunction(num_args=1, implementation=self._set_color),
            "setColorRGB": BuiltinFunction(num_args=3, implementation=self._set_color_RGB),
            "drawPixel": BuiltinFunction(num_args=2, implementation=self._draw_pixel),
            "drawLine": BuiltinFunction(num_args=4, implementation=self._draw_line),
            "drawRectangle": BuiltinFunction(num_args=4, implementation=self._draw_rectangle),
            "drawCircle": BuiltinFunction(num_args=3, implementation=self._draw_circle),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        pygame.display.set_caption("JackE screen")
        pygame.display.set_icon(pygame.image.load(ICON_PATH))
        ScreenLibrary.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        ScreenLibrary._clear_screen([], vm)
        return 0
    
    @staticmethod
    def _clear_screen(args: list[int], vm: VirtualMachine) -> int:
        ScreenLibrary.screen.fill(WHITE)
        pygame.display.update()
        return 0
    
    @staticmethod
    def _set_color(args: list[int], vm: VirtualMachine) -> int:
        is_black = args[0]
        ScreenLibrary.color = BLACK if is_black else WHITE
        return 0
    
    @staticmethod
    def _set_color_RGB(args: list[int], vm: VirtualMachine) -> int:
        r, g, b = args[0], args[1], args[2]
        ScreenLibrary.color = (r, g, b)
        return 0
    
    @staticmethod
    def _draw_pixel(args: list[int], vm: VirtualMachine) -> int:
        x, y = args[0], args[1]
        ScreenLibrary.screen.set_at((x, y), ScreenLibrary.color)
        pygame.display.update()
        return 0
    
    @staticmethod
    def _draw_line(args: list[int], vm: VirtualMachine) -> int:
        x1, y1, x2, y2 = args[0], args[1], args[2], args[3]
        pygame.draw.line(ScreenLibrary.screen, ScreenLibrary.color, (x1, y1), (x2, y2))
        pygame.display.update()
        return 0

    @staticmethod
    def _draw_rectangle(args: list[int], vm: VirtualMachine) -> int:
        x1, y1, x2, y2 = args[0], args[1], args[2], args[3]
        if x2 < x1 or y2 < y1:
            raise ValueError("Первая точка должна находиться левее и выше второй")
        dx, dy = x2 - x1, y2 - y1
        pygame.draw.rect(ScreenLibrary.screen, ScreenLibrary.color, (x1, y1, dx, dy))
        pygame.display.update()
        return 0

    @staticmethod
    def _draw_circle(args: list[int], vm: VirtualMachine) -> int:
        x, y, r = args[0], args[1], args[2]
        if r > 181:
            raise ValueError("Радиус круга не должен превышать 181 пиксель")
        pygame.draw.circle(ScreenLibrary.screen, ScreenLibrary.color, (x, y), r)
        pygame.display.update()
        return 0
