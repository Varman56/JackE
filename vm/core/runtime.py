"""
Hack Virtual Machine Runtime
Эмулятор виртуальной машины из курса Nand to Tetris
"""

from vm.core.instruction import Function, Label
from vm.core.program import Program
from vm.core.memory import VMMemory
from vm.builtin.math import MathLibrary
from vm.builtin.registry import BuiltinRegistry


class VirtualMachine:
    """
    Виртуальная машина Hack
    Выполняет VM инструкции и управляет памятью
    """

    def __init__(self, gui: bool = False, debug: bool = False):
        self.gui = gui
        self.debug = debug
        self.memory = VMMemory()
        self.builtin_registry = BuiltinRegistry()
        self._register_builtin_libraries()

        # Таблица меток (для goto/if-goto)
        self.labels: dict[str, int] = {}

        # Счетчик для уникальных меток (для сравнений)
        self.label_counter = 0

        # Стек вызовов для функций
        self.call_stack = []
        self.return_address_counter = 0

    def _register_builtin_libraries(self):
        self.builtin_registry.register_library(MathLibrary())

    def run_program(self, program: Program):
        """
        Выполняет программу VM

        Args:
            program: объект Program с инструкциями
        """
        # Первый проход: собираем все метки
        self._collect_labels(program)

        # Второй проход: выполняем инструкции
        program._current_instruction_index = 0

        while program._current_instruction_index < len(program.instructions):
            instruction = program.get_current_instruction()

            if instruction.source_file:
                self.memory.set_current_file(instruction.source_file)

            if self.debug:
                print(f"[{program._current_instruction_index}] {instruction}")

            # Выполняем инструкцию
            instruction.execute(self, program)

            # Переходим к следующей инструкции (если инструкция не управляет переходом сама)
            if instruction.should_advance():
                program.next_instruction()

        if self.debug:
            print(
                f"\nПрограмма завершена. Stack pointer: {self.memory.get_stack_pointer()}"
            )

    def _collect_labels(self, program: Program):
        """Собирает все метки и их позиции"""
        self.labels.clear()
        for i, instruction in enumerate(program.instructions):
            if isinstance(instruction, Label):
                self.labels[instruction.name] = i
            elif isinstance(instruction, Function):
                self.labels[instruction.name] = i

    def get_stack_top(self) -> int:
        """Возвращает верхнее значение стека (для отладки)"""
        return self.memory.peek()

    def get_stack(self) -> list:
        """Возвращает содержимое стека (для отладки)"""
        sp = self.memory.get_stack_pointer()
        return self.memory.memory[256:sp]

    def execute_builtin_call(self, function_name: str, num_args: int) -> bool:
        builtin_function = self.builtin_registry.resolve(function_name)
        if builtin_function is None:
            return False

        if num_args != builtin_function.num_args:
            raise ValueError(
                f"Неверное число аргументов для {function_name}: "
                f"ожидалось {builtin_function.num_args}, получено {num_args}"
            )

        args = [self.memory.pop() for _ in range(num_args)][::-1]
        result = builtin_function.implementation(args)
        self.memory.push(result)
        return True
