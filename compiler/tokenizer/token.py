from compiler.tokenizer.token_type import TokenType


class Token:
    """Единичный объект необработанного .jack файла. Терминал с точки зрения грамматики"""

    def __init__(
        self, token_type: TokenType, value: str, row: int = 0, col: int = 0
    ) -> None:
        self.token_type = token_type
        self.val = value
        self.row = row
        self.col = col

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
