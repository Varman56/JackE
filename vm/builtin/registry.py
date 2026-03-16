from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass(frozen=True)
class BuiltinFunction:
    num_args: int
    implementation: Callable[[list[int]], int]


class BuiltinLibrary(Protocol):
    name: str

    def functions(self) -> dict[str, BuiltinFunction]: ...


class BuiltinRegistry:
    def __init__(self):
        self._functions: dict[str, BuiltinFunction] = {}

    def register_library(self, library: BuiltinLibrary):
        for function_name, function in library.functions().items():
            qualified_name = f"{library.name}.{function_name}"
            if qualified_name in self._functions:
                raise ValueError(
                    f"Builtin функция уже зарегистрирована: {qualified_name}"
                )
            self._functions[qualified_name] = function

    def resolve(self, qualified_name: str) -> BuiltinFunction | None:
        return self._functions.get(qualified_name)
