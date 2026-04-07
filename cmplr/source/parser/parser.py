import csv
from tokenizer.tokenizer import Tokenizer
from tokenizer.token_type import TokenType
from tokenizer.token import Token
from grammar.grammar_reader import GrammarReader
from parser.parser_tools import *


class Parser:
    def __init__(self, table_path="cmplr/source/grammar/jack_slr_table.csv", grammar_path="cmplr/source/grammar/grammar"):
        self.reader = GrammarReader(grammar_path)
        self.rules = self.reader.rules
        self.action_table = {}
        self.goto_table = {}
        self._load_table(table_path)

    def _load_table(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames[1:]

            for row in reader:
                state_idx = int(row['State'])
                for symbol in fields:
                    value = row[symbol]
                    if not value:
                        continue

                    if symbol in self.reader.non_terminals:
                        self.goto_table[(state_idx, symbol)] = int(value)
                    else:
                        self.action_table[(state_idx, symbol)] = value

    def _get_lookahead(self, token):
        if token.TokenType == TokenType.keyword or token.TokenType == TokenType.symbol:
            return token.value
        return token.TokenType.name

    def run_parser(self, tokens):
        tokens.append(Token(None, "$"))
        stack = [0]
        i = 0

        while True:
            state = stack[-1]
            token = tokens[i]
            lookahead = self._get_lookahead(token) if token.TokenType else "$"

            action = self.action_table.get((state, lookahead))

            if not action:
                print(f"Syntax Error at row {token.row}, col {token.col}: Unexpected token '{token.value}'")
                return False

            if action.startswith('S'):
                next_state = int(action[1:])
                stack.append(next_state)
                i += 1

            elif action.startswith('R'):
                rule_idx = int(action[1:])
                rule = self.rules[rule_idx]

                for _ in range(len(rule.right)):
                    stack.pop()

                state_before_goto = stack[-1]
                goto_state = self.goto_table.get((state_before_goto, rule.left))
                stack.append(goto_state)

                # print(f"Reduced: {rule}")

            elif action == 'ACC':
                print("Parsing Successful!")
                return True

    def tokenize_and_parse(self, file_path):
        text = open_file(file_path)
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()

        if not tokens:
            return False

        return self.run_parser(tokens)

    def parse_all(self, files):
        for file in files:
            print(f"\\n--- Processing {file} ---")
            success = self.tokenize_and_parse(file)
            if not success:
                # TODO: Show error row and col
                print(f"File {file} failed analysis.")
