from compiler.tokenizer.token import Token
from compiler.tokenizer.token_type import TokenType
from compiler.errors.tokenizer_errors import (
    ERR_TOKEN_UNKNOWN,
    ERR_TOKEN_STRING_CONSTANT_NOT_CLOSED,
    ERR_TOKEN_BAD_SYMBOL,
    ERR_TOKEN_BAD_INTEGER,
    ERR_TOKEN_INVALID_INTEGER,
    ERR_TOKEN_MULTILINE_COMMENTS_NOT_CLOSED,
)


class Tokenizer:
    """Класс для токенизации .jack файла

     Аргументы:
    - text: Текст .jack файла
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.parse_index = 0
        self.cur_row = 1
        self.cur_col = 1
        self.tokens: list[Token] = []

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

    def tokenize(self) -> list[Token]:
        """Попытка токенизации текста файла и вовзрат токенов"""
        self._parse_code()
        return self.get_tokens

    def _trim_left(self) -> None:
        """Очистка комментариев, пробельных символов, переводов строки до следующего токена"""
        while self.parse_index < len(self.text):
            cur_symb = self.text[self.parse_index]
            if cur_symb == "\n":  # \n ignored
                self.parse_index += 1
                self.cur_row += 1
                self.cur_col = 1
            elif cur_symb.isspace():  # Space symbols ignored
                self.parse_index += 1
                self.cur_col += 1
            elif self.parse_index < len(self.text) - 1:  # Comments
                if cur_symb == self.text[self.parse_index + 1] == "/":  # 1-row comments
                    self._skip_until_s("\n")
                    self.parse_index += 1
                    self.cur_col = 1
                    self.cur_row += 1
                elif (
                    cur_symb == "/" and self.text[self.parse_index + 1] == "*"
                ):  # n-row comments
                    if not self._skip_until_s("*/"):
                        raise ERR_TOKEN_MULTILINE_COMMENTS_NOT_CLOSED
                    self.cur_col += 2
                    self.parse_index += 2
                else:
                    break
            else:
                break

    def _skip_until_s(self, substr: str) -> bool:
        """Пропуск любых символов, пока не встретим строку substr"""
        while self.text[self.parse_index : self.parse_index + len(substr)] != substr:
            self.cur_col += 1
            if self.text[self.parse_index] == "\n":
                self.cur_col = 1
                self.cur_row += 1
            self.parse_index += 1
            if self.parse_index + len(substr) - 1 >= len(self.text):
                return False
        return True

    def _parse_code(self) -> None:
        """Попытка токенизации. Двигаемся до следующего токена, пытаемся определить его тип"""
        while self.parse_index < len(self.text):
            self._trim_left()
            if self.parse_index < len(self.text):
                res = (
                    self._parse_symbol()
                    or self._parse_string_constant()
                    or self._parse_integer_constant()
                    or self._parse_identifier_and_keywords()
                )
                if not res:
                    raise ERR_TOKEN_UNKNOWN

    def _parse_symbol(self) -> bool:
        """Попытка токенизации символа"""
        cur_symb = self.text[self.parse_index]
        if cur_symb in self.symbols:
            self.tokens.append(
                Token(TokenType.symbol, cur_symb, self.cur_row, self.cur_col)
            )
            self.parse_index += 1
            self.cur_col += 1
            return True
        return False

    def _parse_string_constant(self) -> bool:
        """Попытка токенизации строк"""
        if self.text[self.parse_index] == '"':
            sb = []
            self.parse_index += 1
            while (
                self.parse_index < len(self.text) and self.text[self.parse_index] != '"'
            ):
                if self.text[self.parse_index] == "\n":
                    raise ERR_TOKEN_BAD_SYMBOL
                sb.append(self.text[self.parse_index])
                self.parse_index += 1
            if (
                self.parse_index == len(self.text)
                and self.text[self.parse_index - 1] != '"'
            ):
                raise ERR_TOKEN_STRING_CONSTANT_NOT_CLOSED
            self.parse_index += 1
            self.tokens.append(
                Token(TokenType.stringConstant, "".join(sb), self.cur_row, self.cur_col)
            )
            self.cur_col += len(sb) + 2
            return True
        return False

    def _parse_integer_constant(self) -> bool:
        """Попытка токенизации целочисленных констант"""
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
                if result <= 32767:  # can be improved with our vm
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
                    raise ERR_TOKEN_BAD_INTEGER
            except ValueError:
                raise ERR_TOKEN_INVALID_INTEGER
        return False

    def _parse_identifier_and_keywords(self) -> bool:
        """Попытка токенизации переменных и ключевых слов"""
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
            if s in self.keywords:
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

    @property
    def get_tokens(self) -> list[Token]:
        return self.tokens.copy()
