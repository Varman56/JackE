# from cmplr.source.parser.parser import Parser
from vm.core.runtime import VirtualMachine
from vm.core.program import Program


def main():
    # parser = Parser().tokenize_and_parse("Square.jack")

    vm = VirtualMachine()
    program = Program([])
    vm.run_program(program)


if __name__ == "__main__":
    main()
