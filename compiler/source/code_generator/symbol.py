from enum import Enum


class SymbolKind(Enum):
    STATIC = "static"
    FIELD = "this"
    ARG = "argument"
    VAR = "local"


class Symbol:
    def __init__(self, name, kind: SymbolKind, index: int, var_type):
        self.name = name
        self.kind = kind
        self.index = index
        self.var_type = var_type
        self.is_class = var_type not in ("int", "boolean", "char")
