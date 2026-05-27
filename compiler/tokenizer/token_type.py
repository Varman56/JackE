from enum import Enum


class TokenType(Enum):
    """Типы токенов jack"""

    keyword = 1
    symbol = 2
    integerConstant = 3
    stringConstant = 4
    identifier = 5
    EOF = 6
