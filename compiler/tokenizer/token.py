from compiler.code_generator.var_types import VarTypes
from compiler.code_generator.vm_writer import VMWriter
from compiler.tokenizer.token_type import TokenType


class Token:
    """Единичный объект необработанного .jack файла. Терминал с точки зрения грамматики"""

    def __init__(
        self, token_type: TokenType, value: str, row: int = 0, col: int = 0, **kwargs
    ) -> None:
        self.token_type = token_type
        self.val = value
        self.row = row
        self.col = col
        self.vm = VMWriter()
        self.kwargs = kwargs
        self.start_token = self

    def __repr__(self) -> str:
        return f"{self.token_type.name} {self.val} ({self.row} {self.col})"

    def get_pos(self) -> tuple[int, int]:
        return self.row, self.col

    def eq_pos(self, other: Token) -> bool:
        return self.row == other.row and self.col == other.col

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.val == other.val and self.token_type == other.token_type

    @property
    def get_typed_var_list(self) -> list[tuple[VarTypes | str, str]]:
        raise NotImplementedError("Use NTwithTypedVarList for get_typed_var_list using")

    @property
    def get_var_list(self) -> list[str]:
        raise NotImplementedError("Use NTwithVarList for get_var_list using")
