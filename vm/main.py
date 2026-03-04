from core.runtime import VirtualMachine
from core.program import Program


def main():

    vm = VirtualMachine()
    program = Program([])
    vm.run_program(program)


if __name__ == "__main__":
    main()
