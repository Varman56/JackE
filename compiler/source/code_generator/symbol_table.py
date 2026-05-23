from compiler.source.code_generator.symbol import SymbolKind, Symbol

from compiler.source.code_generator.non_terminal import NonTerminal


class SymbolTable:
    """Класс таблицы символов файла .jack"""

    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.counts = {kind: 0 for kind in SymbolKind}

    def start_subroutine(self):
        """Очищает таблицу подпрограммы"""
        self.subroutine_symbols = {}
        self.counts[SymbolKind.ARG] = 0
        self.counts[SymbolKind.VAR] = 0

    def define(self, name, type_str, kind):
        """Добавляет переменную в таблицу."""
        target = (
            self.class_symbols
            if kind in [SymbolKind.STATIC, SymbolKind.FIELD]
            else self.subroutine_symbols
        )
        var = Symbol(name=name, kind=kind, index=self.counts[kind], var_type=type_str)
        target[name] = var
        self.counts[kind] += 1

    def var_count(self, kind):
        """Возвращает количество переменных определенного типа"""
        return self.counts[kind]

    def __getitem__(self, var: NonTerminal):
        """Пытается найти функцию по имени, возвращает функцию и нашлась ли она"""
        res = self.subroutine_symbols.get(var.val) or self.class_symbols.get(var.val)
        return res, res is not None
