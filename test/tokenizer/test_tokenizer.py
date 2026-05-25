import pytest
from compiler.tokenizer.tokenizer import Tokenizer, TokenType, Token


class TestTokenizer:
    def setup(self, text):
        self.tokenizer = Tokenizer(text)

    def test_skip_until_symbol(self):
        self.setup("abcedf32")
        self.tokenizer._skip_until_s("c")
        assert self.tokenizer.parse_index == 2

        self.setup("abcedf32")
        self.tokenizer._skip_until_s("ce")
        assert self.tokenizer.parse_index == 2

        self.setup("abcedf32")
        self.tokenizer._skip_until_s("0")
        assert self.tokenizer.parse_index == 8

        self.setup("abcedf32")

        assert not self.tokenizer._skip_until_s("0231346577")

    def test_trim_left(self):
        self.setup("abcedf32")
        self.tokenizer._trim_left()

        assert self.tokenizer.parse_index == 0
        assert self.tokenizer.cur_col == 1
        assert self.tokenizer.cur_row == 1

        self.setup("// comment \n let x = 43")
        self.tokenizer._trim_left()

        assert self.tokenizer.parse_index == 13
        assert self.tokenizer.cur_col == 2
        assert self.tokenizer.cur_row == 2

        self.setup("/*c\nw\nw\nasd */ let x = 43")
        self.tokenizer._trim_left()

        assert self.tokenizer.parse_index == 15
        assert self.tokenizer.cur_col == 8
        assert self.tokenizer.cur_row == 4

        with pytest.raises(SyntaxError):
            self.setup("/*c\nw\nw\nasd let x = 43")
            self.tokenizer._trim_left()

    def test_line_col_number(self):
        text = 'let x=1; // comment\n/*\ncomment 2\n*/\nlet language = "jack" ; '
        self.setup(text)

        expected_tokens = [
            Token(TokenType.keyword, "let", 1, 1),
            Token(TokenType.identifier, "x", 1, 5),
            Token(TokenType.symbol, "=", 1, 6),
            Token(TokenType.integerConstant, "1", 1, 7),
            Token(TokenType.symbol, ";", 1, 8),
            Token(TokenType.keyword, "let", 5, 1),
            Token(TokenType.identifier, "language", 5, 5),
            Token(TokenType.symbol, "=", 5, 14),
            Token(TokenType.stringConstant, "jack", 5, 16),
            Token(TokenType.symbol, ";", 5, 23),
        ]
        tokens = self.tokenizer.tokenize()
        for i, expected in enumerate(expected_tokens):
            assert tokens[i] == expected
            assert tokens[i].eq_pos(expected)
        assert len(tokens) == len(expected_tokens)

