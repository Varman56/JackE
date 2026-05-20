from compiler.source.compiler import Compiler
from vm.core.runtime import VirtualMachine
from vm.core.program import Program


def main():
    # c = Compiler(
    #     "compiler/test/clear_jack/array",
    #     ignore_build_exist=True,
    #     build_grammar=True,
    # )
    # success_files = c.compile()

    vm = VirtualMachine()
    program = Program([])
    vm.run_program(program)


if __name__ == "__main__":
    main()
