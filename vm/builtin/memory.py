from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class MemoryLibrary:
    name = "Memory"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "peek": BuiltinFunction(num_args=1, implementation=self._peek),
            "poke": BuiltinFunction(num_args=2, implementation=self._poke),
            "alloc": BuiltinFunction(num_args=1, implementation=self._alloc),
            "deAlloc": BuiltinFunction(num_args=1, implementation=self._de_alloc),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _peek(args: list[int], vm: VirtualMachine) -> int:
        address = args[0]
        # TODO SCREEN and KBD
        return vm.memory.memory[address]

    @staticmethod
    def _poke(args: list[int], vm: VirtualMachine) -> int:
        address, value = args[0], args[1]
        # TODO SCREEN and KBD
        vm.memory.memory[address] = value
        return 0

    @staticmethod
    def _alloc(args: list[int], vm: VirtualMachine) -> int:
        size = args[0]
        return vm.memory.allocate_heap(size)

    @staticmethod
    def _de_alloc(args: list[int], vm: VirtualMachine) -> int:
        o = args[0]
        vm.memory.free_heap(o)
        return 0
