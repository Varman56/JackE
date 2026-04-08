from enum import Enum

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

    def kind_of(self, name):
        res = self.subroutine_symbols.get(name) or self.class_symbols.get(name)
        return res['kind'] if res else SymbolKind.NONE

    def type_of(self, name):
        res = self.subroutine_symbols.get(name) or self.class_symbols.get(name)
        return res['type'] if res else None

    def index_of(self, name):
        res = self.subroutine_symbols.get(name) or self.class_symbols.get(name)
        return res['index'] if res else None