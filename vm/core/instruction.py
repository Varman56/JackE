from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine
    from vm.core.program import Program


class Instruction:
    """Base class for all VM instructions"""

    def __init__(self):
        self.source_file = "default"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        """
        Выполняет инструкцию

        Args:
            vm: виртуальная машина
            program: программа
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.execute() must be implemented"
        )

    def should_advance(self) -> bool:
        """Должна ли VM автоматически перейти к следующей инструкции"""
        return True


# Stack operations
class Push(Instruction):
    def __init__(self, segment: str, index: int):
        super().__init__()
        self.segment = segment
        self.index = index

    def __repr__(self):
        return f"Push({self.segment}, {self.index})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        value = vm.memory.read_segment(self.segment, self.index)
        vm.memory.push(value)


class Pop(Instruction):
    def __init__(self, segment: str, index: int):
        super().__init__()
        self.segment = segment
        self.index = index

    def __repr__(self):
        return f"Pop({self.segment}, {self.index})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        value = vm.memory.pop()
        vm.memory.write_segment(self.segment, self.index, value)


# Arithmetic operations
class Arithmetic(Instruction):
    pass


class Add(Arithmetic):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(a + b)


class Sub(Arithmetic):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(a - b)


class Neg(Arithmetic):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        a = vm.memory.pop()
        vm.memory.push(-a)


# Logical operations
class Logical(Instruction):
    pass


class And(Logical):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(a & b)


class Or(Logical):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(a | b)


class Not(Logical):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        a = vm.memory.pop()
        vm.memory.push(~a & 0xFFFF)  # 16-bit not


# Comparison operations
class Comparison(Instruction):
    pass


class Eq(Comparison):
    """Equal"""

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(-1 if a == b else 0)  # true = -1, false = 0


class Gt(Comparison):
    """Greater than"""

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(-1 if a > b else 0)


class Lt(Comparison):
    """Less than"""

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        b = vm.memory.pop()
        a = vm.memory.pop()
        vm.memory.push(-1 if a < b else 0)


# Program flow
class Label(Instruction):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Label({self.name})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        # Метки не выполняются, просто пропускаем
        pass


class Goto(Instruction):
    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def __repr__(self):
        return f"Goto({self.label})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        if self.label not in vm.labels:
            raise ValueError(f"Неизвестная метка: {self.label}")
        program.jump_to_instruction(vm.labels[self.label])

    def should_advance(self) -> bool:
        return False


class IfGoto(Instruction):
    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def __repr__(self):
        return f"IfGoto({self.label})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        condition = vm.memory.pop()
        if condition != 0:  # if true (non-zero)
            if self.label not in vm.labels:
                raise ValueError(f"Неизвестная метка: {self.label}")
            program.jump_to_instruction(vm.labels[self.label])
        else:
            program.next_instruction()

    def should_advance(self) -> bool:
        return False


# Function commands
class Function(Instruction):
    def __init__(self, name: str, num_vars: int):
        super().__init__()
        self.name = name
        self.num_vars = num_vars

    def __repr__(self):
        return f"Function({self.name}, {self.num_vars})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        # Инициализируем локальные переменные нулями
        for i in range(self.num_vars):
            vm.memory.push(0)


class Call(Instruction):
    def __init__(self, function_name: str, num_args: int):
        super().__init__()
        self.function_name = function_name
        self.num_args = num_args

    def __repr__(self):
        return f"Call({self.function_name}, {self.num_args})"

    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        if vm.execute_builtin_call(self.function_name, self.num_args):
            program.next_instruction()
            return

        # Сохраняем состояние вызывающей функции
        return_addr = program._current_instruction_index + 1

        # Push return address
        vm.memory.push(return_addr)

        # Push LCL
        vm.memory.push(vm.memory.get_local_pointer())

        # Push ARG
        vm.memory.push(vm.memory.get_arg_pointer())

        # Push THIS
        vm.memory.push(vm.memory.get_this_pointer())

        # Push THAT
        vm.memory.push(vm.memory.get_that_pointer())

        # ARG = SP - 5 - num_args
        sp = vm.memory.get_stack_pointer()
        vm.memory.set_arg_pointer(sp - 5 - self.num_args)

        # LCL = SP
        vm.memory.set_local_pointer(sp)

        # Переход к функции
        if self.function_name not in vm.labels:
            raise ValueError(f"Неизвестная функция: {self.function_name}")
        program.jump_to_instruction(vm.labels[self.function_name])

    def should_advance(self) -> bool:
        return False


class Return(Instruction):
    def execute(self, vm: "VirtualMachine", program: "Program") -> None:
        # Восстанавливаем состояние вызывающей функции
        frame = vm.memory.get_local_pointer()

        # Получаем адрес возврата (в frame-5)
        return_addr = vm.memory.memory[frame - 5]

        # Помещаем возвращаемое значение на место ARG[0]
        return_value = vm.memory.pop()
        arg_base = vm.memory.get_arg_pointer()
        vm.memory.memory[arg_base] = return_value

        # Восстанавливаем SP вызывающей функции
        vm.memory.set_stack_pointer(arg_base + 1)

        # Восстанавливаем THAT, THIS, ARG, LCL
        vm.memory.set_that_pointer(vm.memory.memory[frame - 1])
        vm.memory.set_this_pointer(vm.memory.memory[frame - 2])
        vm.memory.set_arg_pointer(vm.memory.memory[frame - 3])
        vm.memory.set_local_pointer(vm.memory.memory[frame - 4])

        # Переход на адрес возврата
        program.jump_to_instruction(return_addr)

    def should_advance(self) -> bool:
        return False
