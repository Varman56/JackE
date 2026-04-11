from vm.core.instruction import Instruction


class Program:
    def __init__(self, instructions: list[Instruction]):
        self.instructions = instructions
        self._current_instruction_index = 0

    def jump_to_instruction(self, index: int):
        if index < 0 or index >= len(self.instructions):
            raise IndexError("Instruction index out of bounds.")
        self._current_instruction_index = index

    def next_instruction(self):
        self._current_instruction_index += 1

    def get_current_instruction(self) -> Instruction:
        if self._current_instruction_index >= len(self.instructions):
            raise IndexError("No more instructions to execute.")
        return self.instructions[self._current_instruction_index]
