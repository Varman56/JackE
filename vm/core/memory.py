"""
Memory management for Hack VM
Управление сегментами памяти виртуальной машины
"""

from vm.core.screen import ScreenWorker


class VMMemory:
    """
    Управление сегментами памяти Hack VM

    Сегменты памяти:
    - stack: стек для вычислений
    - local: локальные переменные функции
    - argument: аргументы функции
    - this/that: указатели на объекты/массивы
    - temp: временная память (фиксированные адреса 5-12)
    - pointer: указатели на this/that (адреса 3-4)
    - static: статические переменные
    - constant: виртуальный сегмент констант
    """

    # Базовые адреса для сегментов в основной памяти
    SP = 0  # Stack Pointer
    LCL = 1  # Local segment base
    ARG = 2  # Argument segment base
    THIS = 3  # This pointer
    THAT = 4  # That pointer
    TEMP_BASE = 5  # Temp segment base (5-12)
    STATIC_BASE = 16  # Static variables start
    HEAP_START = 2048  # Начало кучи для объектов (Array, String)
    HEAP_LIMIT = 16384  # До экрана Hack RAM
    KBD = 24576  # Регистр, в котором должен храниться код нажатой клавиши клавиатуры

    def __init__(self, screen: ScreenWorker, memory_size: int = 32768):
        """
        Инициализация памяти VM

        Args:
            memory_size: размер памяти (по умолчанию 32K как в Hack)
        """
        # Основная память (RAM)
        self.memory: list[int] = [0] * memory_size

        # Stack pointer - указывает на следующую свободную позицию
        self.memory[self.SP] = 256  # Стек начинается с адреса 256

        # Базовые указатели для сегментов
        self.memory[self.LCL] = 300  # Local
        self.memory[self.ARG] = 400  # Argument
        self.memory[self.THIS] = 3000  # This
        self.memory[self.THAT] = 4000  # That

        # Статические переменные для каждого файла
        self.static_vars: dict[str, list[int]] = {}
        self.current_file = ""
        self.set_current_file("default")

        # Простая куча без переиспользования освобожденных блоков.
        self.heap_next_free = self.HEAP_START
        self.heap_allocations: dict[int, int] = {}
        self.heap_free_blocks: list[tuple[int, int]] = []

        self.screen = screen

    def reset_heap(self):
        """Сбрасывает состояние кучи."""
        self.heap_next_free = self.HEAP_START
        self.heap_allocations.clear()
        self.heap_free_blocks.clear()

    def set_current_file(self, filename: str):
        """Устанавливает текущий файл для static переменных"""
        self.current_file = filename
        if filename not in self.static_vars:
            self.static_vars[filename] = [0] * 240  # Max 240 static vars

    def push(self, value: int):
        """Добавляет значение на стек"""
        sp = self.memory[self.SP]
        self.memory[sp] = value
        self.memory[self.SP] = sp + 1

    def pop(self) -> int:
        """Снимает значение со стека"""
        self.memory[self.SP] -= 1
        sp = self.memory[self.SP]
        return self.memory[sp]

    def peek(self) -> int:
        """Смотрит верхнее значение стека без снятия"""
        sp = self.memory[self.SP] - 1
        return self.memory[sp]

    def get_segment_address(self, segment: str, index: int) -> int:
        """
        Получает адрес в памяти для заданного сегмента и индекса

        Args:
            segment: имя сегмента (local, argument, this, that, temp, pointer, static)
            index: индекс в сегменте

        Returns:
            адрес в основной памяти
        """
        if segment == "local":
            return self.memory[self.LCL] + index
        elif segment == "argument":
            return self.memory[self.ARG] + index
        elif segment == "this":
            return self.memory[self.THIS] + index
        elif segment == "that":
            return self.memory[self.THAT] + index
        elif segment == "temp":
            if index > 7:
                raise ValueError(f"temp index out of range: {index}")
            return self.TEMP_BASE + index
        elif segment == "pointer":
            if index == 0:
                return self.THIS
            elif index == 1:
                return self.THAT
            else:
                raise ValueError(f"pointer index must be 0 or 1, got: {index}")
        elif segment == "static":
            # Static переменные хранятся отдельно для каждого файла
            return None  # Обрабатывается отдельно
        else:
            raise ValueError(f"Unknown segment: {segment}")

    def read_segment(self, segment: str, index: int) -> int:
        """Читает значение из сегмента"""
        if segment == "constant":
            return index  # Константы - это просто значения
        elif segment == "static":
            return self.static_vars[self.current_file][index]
        else:
            addr = self.get_segment_address(segment, index)
            return self.read_memory(addr)
            # return self.memory[addr]

    def read_memory(self, address: int) -> int:
        if address < self.HEAP_LIMIT or address > self.KBD:
            return self.memory[address]
        elif address == self.KBD:
            return self.screen.key_pressed()
        else:
            return self.screen.read_screen(address - self.HEAP_LIMIT)

    def write_segment(self, segment: str, index: int, value: int):
        """Записывает значение в сегмент"""
        if segment == "constant":
            raise ValueError("Cannot write to constant segment")
        elif segment == "static":
            self.static_vars[self.current_file][index] = value
        else:
            addr = self.get_segment_address(segment, index)
            self.write_memory(addr, value)
            # self.memory[addr] = value

    def write_memory(self, address: int, value: int) -> None:
        if address < self.HEAP_LIMIT or address > self.KBD:
            self.memory[address] = value
        elif address == self.KBD:
            self.screen.set_key_pressed(value)
        else:
            self.screen.write_screen(address - self.HEAP_LIMIT, value)

    def get_stack_pointer(self) -> int:
        """Возвращает текущее значение stack pointer"""
        return self.memory[self.SP]

    def set_stack_pointer(self, value: int):
        """Устанавливает stack pointer"""
        self.memory[self.SP] = value

    def get_local_pointer(self) -> int:
        """Возвращает указатель на local сегмент"""
        return self.memory[self.LCL]

    def set_local_pointer(self, value: int):
        """Устанавливает указатель на local сегмент"""
        self.memory[self.LCL] = value

    def get_arg_pointer(self) -> int:
        """Возвращает указатель на argument сегмент"""
        return self.memory[self.ARG]

    def set_arg_pointer(self, value: int):
        """Устанавливает указатель на argument сегмент"""
        self.memory[self.ARG] = value

    def get_this_pointer(self) -> int:
        """Возвращает THIS указатель"""
        return self.memory[self.THIS]

    def set_this_pointer(self, value: int):
        """Устанавливает THIS указатель"""
        self.memory[self.THIS] = value

    def get_that_pointer(self) -> int:
        """Возвращает THAT указатель"""
        return self.memory[self.THAT]

    def set_that_pointer(self, value: int):
        """Устанавливает THAT указатель"""
        self.memory[self.THAT] = value

    def allocate_heap(self, words: int) -> int:
        """Выделяет блок в куче и возвращает базовый адрес."""
        if words <= 0:
            raise ValueError(f"Heap allocation size must be positive, got: {words}")

        for i, (base, size) in enumerate(self.heap_free_blocks):
            if size < words:
                continue

            base_address = base
            if size == words:
                del self.heap_free_blocks[i]
            else:
                self.heap_free_blocks[i] = (base + words, size - words)

            self.heap_allocations[base_address] = words
            for address in range(base_address, base_address + words):
                self.memory[address] = 0
            return base_address

        base_address = self.heap_next_free
        end_address = base_address + words

        if end_address > self.HEAP_LIMIT:
            raise ValueError(
                f"Heap overflow: requested {words} words, available {self.HEAP_LIMIT - self.heap_next_free}"
            )

        self.heap_allocations[base_address] = words
        self.heap_next_free = end_address

        for address in range(base_address, end_address):
            self.memory[address] = 0

        return base_address

    def free_heap(self, base_address: int):
        """Освобождает ранее выделенный блок кучи."""
        if base_address == 0:
            return

        words = self.heap_allocations.pop(base_address, None)
        if words is None:
            raise ValueError(f"Unknown heap allocation address: {base_address}")

        for address in range(base_address, base_address + words):
            self.memory[address] = 0

        self._add_free_block(base_address, words)

    def _add_free_block(self, base_address: int, words: int):
        if words <= 0:
            return

        index = 0
        while (
            index < len(self.heap_free_blocks)
            and self.heap_free_blocks[index][0] < base_address
        ):
            index += 1

        self.heap_free_blocks.insert(index, (base_address, words))

        if index > 0:
            prev_base, prev_size = self.heap_free_blocks[index - 1]
            if prev_base + prev_size == base_address:
                base_address = prev_base
                words += prev_size
                self.heap_free_blocks[index - 1 : index + 1] = [(base_address, words)]
                index -= 1

        if index + 1 < len(self.heap_free_blocks):
            next_base, next_size = self.heap_free_blocks[index + 1]
            if base_address + words == next_base:
                self.heap_free_blocks[index : index + 2] = [
                    (base_address, words + next_size)
                ]
