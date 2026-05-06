import csv

from compiler.source.errors.parser_errors import ERR_UNEXPECTED_STATE
from compiler.source.code_generator.code_generator import CodeGenerator
from compiler.source.code_generator.vm_writer import VMWriter
from compiler.source.tokenizer.tokenizer import Tokenizer, TokenType, Token
from compiler.source.grammar.grammar_reader import GrammarReader


class Parser:
    def __init__(self, grammar_file, states_file, pout=print):
        self.reader = GrammarReader(grammar_file)  # TODO: Generate one grammar.slr file, without using reader here
        self.rules = self.reader.rules
        self.action_table = {}
        self.goto_table = {}
        self._load_table(states_file)
        self.generator = CodeGenerator(VMWriter())
        self.pout = pout

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
        if token.token_type in (TokenType.keyword, TokenType.symbol):
            return token.val
        return token.token_type.name

    def run_parser(self, tokens):
        tokens.append(Token(None, "$"))  # TODO: replace with TokenType.END
        stack = [0]
        value_stack = []

        i = 0
        while True:
            state = stack[-1]
            token = tokens[i]
            lookahead = self._get_lookahead(
                token) if token.token_type else "$"  # TODO: check problem of string "$" in .jack code

            action = self.action_table.get((state, lookahead))
            if not action:
                self.pout(
                    f"Syntax Error at row {token.row}, col {token.col}: Unexpected token '{token.val}'")  # TODO: check panic with None TokenType in "$"
                return False

            if action.startswith('S'):
                next_state = int(action[1:])
                stack.append(next_state)
                value_stack.append(token)
                i += 1
            elif action.startswith('R'):
                rule_idx = int(action[1:])
                rule = self.rules[rule_idx]

                args = []
                for _ in range(len(rule.right)):  # TODO: check panic when value_stack/stack empty
                    stack.pop()
                    args.append(value_stack.pop())
                args.reverse()

                result = self.generator.generate(rule, args)  # return string, list, None!!!

                state_before = stack[-1]
                goto_state = self.goto_table.get((state_before, rule.left))
                stack.append(goto_state)
                value_stack.append(result)
            elif action == 'ACC':
                return True
            else:
                raise ERR_UNEXPECTED_STATE

    def tokenize_and_parse(self, text):
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()
        if not tokens:
            return False
        return self.run_parser(tokens)

    def parse(self, text):
        self.generator = CodeGenerator(VMWriter())
        return self.tokenize_and_parse(text), self.generator.vm.get_collected() # TODO: check generator's vm
