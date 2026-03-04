import pytest
from cmplr.source.tokenizer.Tokenizer import Tokenizer


class TestTokenizer:
    def setup(self, text):
        self.tokenizer = Tokenizer(text)

    def test_skip_until_symbol(self):
        self.setup('abcedf32')
        self.tokenizer.skip_until_s("c")
        assert self.tokenizer.parse_index == 2

        self.setup('abcedf32')
        self.tokenizer.skip_until_s("ce")
        assert self.tokenizer.parse_index == 2

        self.setup('abcedf32')
        self.tokenizer.skip_until_s("0")
        assert self.tokenizer.parse_index == 8

        self.setup('abcedf32')

        assert not self.tokenizer.skip_until_s("0231346577")

    def test_trim_left(self):
        self.setup('abcedf32')
        self.tokenizer.trim_left()

        assert self.tokenizer.parse_index == 0
        assert self.tokenizer.cur_col == 0
        assert self.tokenizer.cur_row == 0

        self.setup('// comment \n let x = 43')
        self.tokenizer.trim_left()

        assert self.tokenizer.parse_index == 13
        assert self.tokenizer.cur_col == 1
        assert self.tokenizer.cur_row == 1

        self.setup('/*c\nw\nw\nasd */ let x = 43')
        self.tokenizer.trim_left()

        assert self.tokenizer.parse_index == 15
        assert self.tokenizer.cur_col == 7
        assert self.tokenizer.cur_row == 3

        with pytest.raises(SyntaxError):
            self.setup('/*c\nw\nw\nasd let x = 43')
            self.tokenizer.trim_left()
