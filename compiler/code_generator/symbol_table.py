from compiler.code_generator.symbol import SymbolKind, Symbol

from compiler.code_generator.non_terminal import NonTerminal
from compiler.code_generator.var_types import VarTypes


class SymbolTable:
    """Класс таблицы символов файла .jack"""

    def __init__(self) -> None:
        self.class_symbols: dict[str, Symbol] = {}
        self.subroutine_symbols: dict[str, Symbol] = {}
        self.counts = {kind: 0 for kind in SymbolKind}

    def start_subroutine(self) -> None:
        """Очищает таблицу подпрограммы"""
        self.subroutine_symbols = {}
        self.counts[SymbolKind.ARG] = 0
        self.counts[SymbolKind.VAR] = 0

    def define(self, name: str, var_type: VarTypes | str, kind: SymbolKind) -> None:
        """Добавляет переменную в таблицу."""
        target = (
            self.class_symbols
            if kind in [SymbolKind.STATIC, SymbolKind.FIELD]
            else self.subroutine_symbols
        )
        var = Symbol(name=name, kind=kind, index=self.counts[kind], var_type=var_type)
        target[name] = var
        self.counts[kind] += 1

    def var_count(self, kind: SymbolKind) -> int:
        """Возвращает количество переменных определенного типа"""
        return self.counts[kind]

    def __getitem__(self, var: NonTerminal) -> tuple[Symbol | None, bool]:
        """Пытается найти функцию по имени, возвращает функцию и нашлась ли она"""
        res = self.subroutine_symbols.get(var.val) or self.class_symbols.get(var.val)
        return res, res is not None
