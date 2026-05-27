from time import sleep
from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class VMError(Exception):
    pass


class SysLibrary:
    name = "Sys"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "halt": BuiltinFunction(num_args=0, implementation=self._halt),
            "error": BuiltinFunction(num_args=1, implementation=self._error),
            "wait": BuiltinFunction(num_args=1, implementation=self._wait),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _halt(args: list[int], vm: VirtualMachine) -> int:
        vm.screen.close_screen()
        return 0

    @staticmethod
    def _error(args: list[int], vm: VirtualMachine) -> int:
        error_code = args[0]
        raise VMError(f"ERR<{error_code}>")
        return 0

    @staticmethod
    def _wait(args: list[int], vm: VirtualMachine) -> int:
        duration = args[0]
        sleep(duration / 1000)
        return 0
