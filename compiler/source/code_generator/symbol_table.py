from enum import Enum

from compiler.source.code_generator.non_terminal import NonTerminal
from compiler.source.errors.code_generator_errors import ErrUnknownSymbol


class SymbolKind(Enum):
    STATIC = "static"
    FIELD = "this"
    ARG = "argument"
    VAR = "local"
    NONE = "none"


class SymbolTable:
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
        target = self.class_symbols if kind in [SymbolKind.STATIC, SymbolKind.FIELD] else self.subroutine_symbols
        target[name] = {'type': type_str, 'kind': kind, 'index': self.counts[kind]}
        self.counts[kind] += 1

    def var_count(self, kind):
        return self.counts[kind]

    def _check_unknown_symbol(self, var: NonTerminal):
        name = var.get_val()
        if name not in self.subroutine_symbols and name not in self.class_symbols:
            raise ErrUnknownSymbol(var.start_token.row, var.start_token.col)

    def kind_of(self, var: NonTerminal):
        self._check_unknown_symbol(var)
        res = self.subroutine_symbols.get(var.get_val()) or self.class_symbols.get(var.get_val())
        return res['kind']

    def __getitem__(self, var : NonTerminal):
        self._check_unknown_symbol(var)
        res = self.subroutine_symbols.get(var.get_val()) or self.class_symbols.get(var.get_val())
        return res['kind'], res['index']

    def get_subroutine(self, name: str):
        res = self.subroutine_symbols.get(name)
        return res['kind'], res['index']

    def type_of(self, var: NonTerminal):
        self._check_unknown_symbol(var)
        name = var.get_val()
        res = self.subroutine_symbols.get(name) or self.class_symbols.get(name)
        return res['type']

    def index_of(self, var: NonTerminal):
        self._check_unknown_symbol(var)
        name = var.get_val()
        res = self.subroutine_symbols.get(name) or self.class_symbols.get(name)
        return res['index']
