from cmplr.source.tokenizer.token_type import TokenType
from cmplr.source.tokenizer.token import Token


class TestToken:
    def setup(self, token_type, value):
        self.token = Token(token_type, value)

    def test_str(self):
        self.setup(TokenType.stringConstant, "string_value")
        assert str(self.token) == "<stringConstant> string_value </stringConstant>"

        self.setup(TokenType.integerConstant, 7)
        assert str(self.token) == "<integerConstant> 7 </integerConstant>"

        self.setup(TokenType.keyword, "for")
        assert str(self.token) == "<keyword> for </keyword>"

        self.setup(TokenType.symbol, "~")
        assert str(self.token) == "<symbol> ~ </symbol>"
