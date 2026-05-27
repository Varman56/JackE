from enum import StrEnum


class VarTypes(StrEnum):
    """класс типов данных Jack"""

    int = "int"
    char = "char"
    boolean = "boolean"
    className = "ClassName"
    unknown = "unknown"

    def __str__(self) -> str:
        return self.value
