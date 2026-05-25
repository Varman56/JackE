from compiler.code_generator.var_types import VarTypes
from compiler.precompile.subroutine_kind import SubroutineKind


class Subroutine:
    """Класс для сохранения функций языка jack

    Аргументы:
    - class_name: Имя класса, в котором находится функция.
    - sub_name: Имя функции внутри класса
    - kind: Вид функции
    - params_count: Количество параметров, котоыре принимает, функция
    - res_type: Тип параметра, возвращаемого функцией"""

    def __init__(
        self,
        class_name: str,
        sub_name: str,
        kind: SubroutineKind,
        params_count: int,
        res_type: VarTypes | str,
    ):
        # self.arg_types = [] # TODO: type checking
        self.class_name = class_name
        self.sub_name = sub_name
        self.kind = kind
        self.nargs = params_count
        self.rtype = res_type

    def get_nargs(self) -> int:
        """У метода 0 аргумент - this"""
        if self.kind == SubroutineKind.method:
            return self.nargs + 1
        return self.nargs

    def get_full_name(self) -> str:
        return f"{self.class_name}.{self.sub_name}"

    def __repr__(self) -> str:
        return f"{self.kind.name} {self.get_full_name()}({self.nargs}) {self.rtype}"
