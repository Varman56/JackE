class Token:
    def __init__(self, token_type, value, row=0, col=0):
        self.TokenType = token_type
        self.value = value
        self.row = row
        self.col = col

    def __str__(self):
        return f"<{self.TokenType.name}> {self.value} </{self.TokenType.name}>"

    def get_pos(self):
        return self.row, self.col