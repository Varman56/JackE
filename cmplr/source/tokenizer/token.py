class Token:
    def __init__(self, token_type, value, row=0, col=0):
        self.TokenType = token_type
        self.value = value
        self.row = row
        self.col = col

    def __repr__(self):
        return f"{self.TokenType.name} {self.value} ({self.row} {self.col})"

    def get_pos(self):
        return self.row, self.col

    def __eq__(self, other):
        return self.value == other.value and self.TokenType == other.TokenType

    def eq_pos(self, other):
        return self.row == other.row and self.col == other.col