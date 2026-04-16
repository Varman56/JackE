from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class ArrayLibrary:
    name = "Array"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "new": BuiltinFunction(num_args=1, implementation=self._new),
            "dispose": BuiltinFunction(num_args=1, implementation=self._dispose),
        }

    def _new(self, args: list[int], vm: VirtualMachine) -> int:
        size = args[0]
        if size < 0:
            raise ValueError("Array.new: отрицательный размер")

        words_to_allocate = size if size > 0 else 1
        return vm.memory.allocate_heap(words_to_allocate)

    def _dispose(self, args: list[int], vm: VirtualMachine) -> int:
        base_address = args[0]
        vm.memory.free_heap(base_address)

        return 0
