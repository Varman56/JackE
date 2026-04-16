import math
from typing import TYPE_CHECKING

from vm.builtin.registry import BuiltinFunction

if TYPE_CHECKING:
    from vm.core.runtime import VirtualMachine


class MathLibrary:
    name = "Math"

    def functions(self) -> dict[str, BuiltinFunction]:
        return {
            "init": BuiltinFunction(num_args=0, implementation=self._init),
            "abs": BuiltinFunction(num_args=1, implementation=self._abs),
            "multiply": BuiltinFunction(num_args=2, implementation=self._multiply),
            "divide": BuiltinFunction(num_args=2, implementation=self._divide),
            "min": BuiltinFunction(num_args=2, implementation=self._min),
            "max": BuiltinFunction(num_args=2, implementation=self._max),
            "sqrt": BuiltinFunction(num_args=1, implementation=self._sqrt),
        }

    @staticmethod
    def _init(args: list[int], vm: VirtualMachine) -> int:
        return 0

    @staticmethod
    def _abs(args: list[int], vm: VirtualMachine) -> int:
        return abs(args[0])

    @staticmethod
    def _multiply(args: list[int], vm: VirtualMachine) -> int:
        left, right = args
        return left * right

    @staticmethod
    def _divide(args: list[int], vm: VirtualMachine) -> int:
        left, right = args
        if right == 0:
            raise ValueError("Math.divide: деление на ноль")
        return left // right

    @staticmethod
    def _min(args: list[int], vm: VirtualMachine) -> int:
        left, right = args
        return left if left <= right else right

    @staticmethod
    def _max(args: list[int], vm: VirtualMachine) -> int:
        left, right = args
        return left if left >= right else right

    @staticmethod
    def _sqrt(args: list[int], vm: VirtualMachine) -> int:
        value = args[0]
        if value < 0:
            raise ValueError("Math.sqrt: отрицательный аргумент")
        return math.isqrt(value)
