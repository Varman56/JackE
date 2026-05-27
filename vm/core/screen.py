from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from threading import Thread, Event
from queue import Queue

import pygame


FPS = 60
WIDTH, HEIGHT = 512, 256
WINDOW_TITLE = "JackE screen"
ICON_PATH = "JackE_icon.bmp"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class CommandType(Enum):
    CLEAR_SCREEN = "clearScreen"
    SET_COLOR = "setColor"
    DRAW_PIXEL = "drawPixel"
    DRAW_LINE = "drawLine"
    DRAW_RECTANGLE = "drawRectangle"
    DRAW_CIRCLE = "drawCircle"
    CLEAR_RECTANGLE = "clearRectangle"


@dataclass(frozen=True)
class Command:
    command_type: CommandType
    args: list[int] = field(default_factory=list)
    answer_queue: Queue[int] = field(default_factory=Queue)


@lru_cache(1)
class ScreenWorker(Thread):
    def __init__(self) -> None:
        super().__init__()

        self.ready = Event()
        self.running = Event()

        self.commands: Queue[Command] = Queue()

        self.screen: pygame.Surface | None = None
        self.color: tuple[int, int, int] = BLACK
        self.clock: pygame.time.Clock | None = None

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_icon(pygame.image.load(ICON_PATH))

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.color = BLACK
        self.clock = pygame.time.Clock()

        self._clear_screen()

        self.ready.set()
        self.running.set()

        while self.running.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running.clear()
                self._process_commands()
                pygame.display.update()
                self.clock.tick(FPS)

        pygame.quit()

    def _process_commands(self) -> None:
        while not self.commands.empty():
            command = self.commands.get()
            match command.command_type:
                case CommandType.CLEAR_SCREEN:
                    self._clear_screen()
                case CommandType.SET_COLOR:
                    self._set_color(*command.args)
                case CommandType.DRAW_PIXEL:
                    self._draw_pixel(*command.args)
                case CommandType.DRAW_LINE:
                    self._draw_line(*command.args)
                case CommandType.DRAW_RECTANGLE:
                    self._draw_rectangle(*command.args)
                case CommandType.DRAW_CIRCLE:
                    self._draw_circle(*command.args)
                case CommandType.CLEAR_RECTANGLE:
                    self._clear_rectangle(*command.args)

    def close_screen(self) -> None:
        self.running.clear()
        self.join()

    def _clear_screen(self) -> None:
        self.screen.fill(WHITE)

    def _set_color(self, r: int, g: int, b: int) -> None:
        self.color = (r, g, b)

    def _draw_pixel(self, x: int, y: int) -> None:
        self.screen.set_at((x, y), self.color)

    def _draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        pygame.draw.line(self.screen, self.color, (x1, y1), (x2, y2))

    def _draw_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if x2 < x1 or y2 < y1:
            raise ValueError("Первая точка должна находиться левее и выше второй")
        dx, dy = x2 - x1 + 1, y2 - y1 + 1
        pygame.draw.rect(self.screen, self.color, (x1, y1, dx, dy))

    def _draw_circle(self, x: int, y: int, r: int) -> None:
        if r > 181:
            raise ValueError("Радиус круга не должен превышать 181 пиксель")
        pygame.draw.circle(self.screen, self.color, (x, y), r)

    def _clear_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if x2 < x1 or y2 < y1:
            raise ValueError("Первая точка должна находиться левее и выше второй")
        dx, dy = x2 - x1 + 1, y2 - y1 + 1
        pygame.draw.rect(self.screen, WHITE, (x1, y1, dx, dy))

    def clear_screen(self) -> None:
        self.commands.put(Command(CommandType.CLEAR_SCREEN))

    def set_color(self, r: int, g: int, b: int) -> None:
        self.commands.put(Command(CommandType.SET_COLOR, [r, g, b]))

    def draw_pixel(self, x: int, y: int) -> None:
        self.commands.put(Command(CommandType.DRAW_PIXEL, [x, y]))

    def draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.commands.put(Command(CommandType.DRAW_LINE, [x1, y1, x2, y2]))

    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.commands.put(Command(CommandType.DRAW_RECTANGLE, [x1, y1, x2, y2]))

    def draw_circle(self, x: int, y: int, r: int) -> None:
        self.commands.put(Command(CommandType.DRAW_CIRCLE, [x, y, r]))

    def clear_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.commands.put(Command(CommandType.CLEAR_RECTANGLE, [x1, y1, x2, y2]))
