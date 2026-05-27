from tokenizer.token import Token
from tokenizer.token_type import TokenType


class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.parse_index = 0
        self.cur_row = 0
        self.cur_col = 0
        self.tokenStack = []
        self.tokens = []

        self.keywords = {
            "class",
            "constructor",
            "function",
            "method",
            "field",
            "static",
            "var",
            "int",
            "char",
            "boolean",
            "void",
            "true",
            "false",
            "null",
            "this",
            "let",
            "do",
            "if",
            "else",
            "while",
            "return",
        }
        self.symbols = set("{}()[].,;+-*/&|<>=~")

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

    def parse_code(self):
        while self.parse_index < len(self.text):
            self.trim_left()
            if self.parse_index < len(self.text):
                res = (
                    self.parse_symbol()
                    or self.parse_string_constant()
                    or self.parse_integer_constant()
                    or self.parse_identifier_and_keywords()
                )
                if not res:
                    raise ValueError("Token cant be parsed")

    def parse_symbol(self):
        cur_symb = self.text[self.parse_index]
        if cur_symb in self.symbols:
            self.tokens.append(
                Token(TokenType.symbol, cur_symb, self.cur_row, self.cur_col)
            )
            self.parse_index += 1
            self.cur_col += 1
            return True
        return False

    def parse_string_constant(self):
        if self.text[self.parse_index] == '"':
            sb = []
            self.parse_index += 1
            while (
                self.parse_index < len(self.text) and self.text[self.parse_index] != '"'
            ):
                if self.text[self.parse_index] == "\n":
                    raise ValueError("Newline in string constant")
                sb.append(self.text[self.parse_index])
                self.parse_index += 1
            if (
                self.parse_index == len(self.text)
                and self.text[self.parse_index - 1] != '"'
            ):
                raise ValueError("Unterminated string constant")  # TODO: test+check
            self.parse_index += 1
            self.tokens.append(
                Token(TokenType.stringConstant, "".join(sb), self.cur_row, self.cur_col)
            )
            self.cur_col += len(sb)
            return True
        return False

    def parse_integer_constant(self):
        if self.text[self.parse_index].isdigit():
            sb = list()
            sb.append(self.text[self.parse_index])
            self.parse_index += 1
            while (
                self.parse_index < len(self.text)
                and self.text[self.parse_index].isdigit()
            ):
                sb.append(self.text[self.parse_index])
                self.parse_index += 1
            num_str = "".join(sb)
            try:
                result = int(num_str)
                if result <= 32767:  # TODO: for JackE should be large
                    self.tokens.append(
                        Token(
                            TokenType.integerConstant,
                            num_str,
                            self.cur_row,
                            self.cur_col,
                        )
                    )
                    self.cur_col += len(sb)
                    return True
                else:
                    raise ValueError("Integer constant too large")
            except ValueError:
                raise ValueError("Invalid integer constant")
        return False

    def parse_identifier_and_keywords(self):
        cur_symb = self.text[self.parse_index]
        if (cur_symb.isalpha() and "A" <= cur_symb <= "z") or cur_symb == "_":
            sb = []
            while True:
                if not (
                    (cur_symb.isalpha() and "A" <= cur_symb <= "z")
                    or cur_symb.isdigit()
                    or cur_symb == "_"
                ):
                    break
                sb.append(self.text[self.parse_index])
                self.parse_index += 1
                if self.parse_index >= len(self.text):
                    break
                cur_symb = self.text[self.parse_index]
            s = "".join(sb)
            if s.lower() in self.keywords:
                self.tokens.append(
                    Token(TokenType.keyword, s, self.cur_row, self.cur_col)
                )
            else:
                self.tokens.append(
                    Token(TokenType.identifier, s, self.cur_row, self.cur_col)
                )
            self.cur_col += len(sb)
            return True
        return False

    def get_tokens(self):
        return self.tokens.copy()

    def __str__(self):
        return self.text[self.parse_index :]
