class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.parse_index = 0
        self.cur_row = 0
        self.cur_col = 0
        self.tokens = []

    def tokenize(self):
        pass

    def trim_left(self):
        while self.parse_index < len(self.text):
            cur_symb = self.text[self.parse_index]
            if cur_symb.isspace():  # Space symbols ignored
                self.parse_index += 1
                self.cur_col += 1
            elif cur_symb == "\n":  # \n ignored
                self.parse_index += 1
                self.cur_row += 1
                self.cur_col = 0
            elif self.parse_index < len(self.text) - 1:  # Comments
                if cur_symb == self.text[self.parse_index + 1] == "/":  # 1-row comments
                    self.skip_until_s("\n")
                    self.parse_index += 1
                    self.cur_col = 0
                    self.cur_row += 1
                elif (
                    cur_symb == "/" and self.text[self.parse_index + 1] == "*"
                ):  # n-row comments
                    if not self.skip_until_s("*/"):
                        raise SyntaxError("Multiline comments should be closed")
                    self.cur_col += 2
                    self.parse_index += 2
                else:
                    break
            else:
                break

    def skip_until_s(self, substr):
        while self.text[self.parse_index : self.parse_index + len(substr)] != substr:
            self.cur_col += 1
            if self.text[self.parse_index] == "\n":
                self.cur_col = 0
                self.cur_row += 1
            self.parse_index += 1
            if self.parse_index + len(substr) - 1 >= len(self.text):
                return False
        return True

    def __str__(self):
        return self.text[self.parse_index :]
