from compiler.source.tokenizer.token_type import TokenType


class Token:
    def __init__(self, token_type: TokenType, value, row=0, col=0):
        self.token_type = token_type
        self.val = value
        self.row = row
        self.col = col

    def __repr__(self):
        return f"{self.token_type.name} {self.val} ({self.row} {self.col})"

    def get_pos(self):
        return self.row, self.col

    def __eq__(self, other):
        return self.val == other.val and self.token_type == other.token_type

    def eq_pos(self, other):
        return self.row == other.row and self.col == other.col