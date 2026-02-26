from core.program import Program


class VirtualMachine:
    def __init__(self, gui: bool = False):
        self.gui = gui

    def run_program(self, program: Program):
        pass