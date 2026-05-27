"""
VM Parser - парсит VM код построчно и создает объекты инструкций
"""

from pathlib import Path

from vm.core.instruction import (
    Add,
    And,
    Call,
    Eq,
    Function,
    Goto,
    Gt,
    IfGoto,
    Instruction,
    Label,
    Lt,
    Neg,
    Not,
    Or,
    Pop,
    Push,
    Return,
    Sub,
)
from vm.core.program import Program


class VMParser:
    """Парсер для чтения и преобразования VM байт-кода в инструкции"""

    def __init__(self):
        self.instructions: list[Instruction] = []
        self.current_function: str | None = None

    def parse_file(self, filepath: str) -> Program:
        """Читает VM файл и создает программу"""
        with open(filepath, "r") as f:
            lines = f.readlines()

        return self.parse_lines(lines, source_file=Path(filepath).stem)

    def parse_lines(self, lines: list[str], source_file: str = "default") -> Program:
        """Парсит список строк VM кода"""
        self.instructions = []
        self.current_function = None

        for line_num, line in enumerate(lines, 1):
            # Удаляем комментарии и пробелы
            line = line.split("//")[0].strip()

            # Пропускаем пустые строки
            if not line:
                continue

            try:
                instruction = self._parse_line(line)
                if instruction:
                    instruction.source_file = source_file
                    self.instructions.append(instruction)
            except Exception as e:
                raise ValueError(f"Ошибка парсинга на строке {line_num}: {line}\n{e}")

        return Program(self.instructions)

    def _qualify_label(self, label: str) -> str:
        if self.current_function:
            return f"{self.current_function}${label}"
        return label

    def _parse_line(self, line: str) -> Instruction:
        """Парсит одну строку VM кода"""
        parts = line.split()
        command = parts[0]

        # Arithmetic and logical commands
        if command == "add":
            return Add()
        elif command == "sub":
            return Sub()
        elif command == "neg":
            return Neg()
        elif command == "and":
            return And()
        elif command == "or":
            return Or()
        elif command == "not":
            return Not()

        # Comparison commands
        elif command == "eq":
            return Eq()
        elif command == "gt":
            return Gt()
        elif command == "lt":
            return Lt()

        # Stack commands
        elif command == "push":
            if len(parts) != 3:
                raise ValueError(f"push требует 2 аргумента: {line}")
            segment = parts[1]
            index = int(parts[2])
            return Push(segment, index)

        elif command == "pop":
            if len(parts) != 3:
                raise ValueError(f"pop требует 2 аргумента: {line}")
            segment = parts[1]
            index = int(parts[2])
            return Pop(segment, index)

        # Program flow
        elif command == "label":
            if len(parts) != 2:
                raise ValueError(f"label требует 1 аргумент: {line}")
            return Label(self._qualify_label(parts[1]))

        elif command == "goto":
            if len(parts) != 2:
                raise ValueError(f"goto требует 1 аргумент: {line}")
            return Goto(self._qualify_label(parts[1]))

        elif command == "if-goto":
            if len(parts) != 2:
                raise ValueError(f"if-goto требует 1 аргумент: {line}")
            return IfGoto(self._qualify_label(parts[1]))

        # Function commands
        elif command == "function":
            if len(parts) != 3:
                raise ValueError(f"function требует 2 аргумента: {line}")
            self.current_function = parts[1]
            return Function(parts[1], int(parts[2]))

        elif command == "call":
            if len(parts) != 3:
                raise ValueError(f"call требует 2 аргумента: {line}")
            return Call(parts[1], int(parts[2]))

        elif command == "return":
            return Return()

        else:
            raise ValueError(f"Неизвестная команда: {command}")
