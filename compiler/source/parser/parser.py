import csv

from compiler.source.errors.parser_errors import ERR_UNEXPECTED_STATE
from compiler.source.code_generator.code_generator import CodeGenerator
from compiler.source.tokenizer.tokenizer import Tokenizer, TokenType, Token
from compiler.source.grammar.grammar_reader import GrammarReader
from compiler.source.precompile.subroutine import SubroutineKind, Subroutine


class Parser:
    def __init__(self, grammar_file, states_file, pout=print):
        self.reader = GrammarReader(
            grammar_file
        )  # TODO: Generate one grammar.slr file, without using reader here
        self.rules = self.reader.rules
        self.action_table = {}
        self.goto_table = {}
        self._load_table(states_file)
        self.generator = None
        self.pout = pout
        self.label_index = 0

    def _load_table(self, path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames[1:]
            for row in reader:
                state_idx = int(row["State"])
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
            lookahead = (
                self._get_lookahead(token) if token.token_type else "$"
            )  # TODO: check problem of string "$" in .jack code

            action = self.action_table.get((state, lookahead))
            if not action:
                self.pout(
                    f"Syntax Error at row {token.row}, col {token.col}: Unexpected token '{token.val}'"
                )  # TODO: check panic with None TokenType in "$"
                return False

            if action.startswith("S"):
                next_state = int(action[1:])
                stack.append(next_state)
                value_stack.append(token)
                if len(value_stack) >= 2:
                    if value_stack[-2].val == "method":
                        self.generator.current_kind = "method"
                    elif value_stack[-2].val == "constructor":
                        self.generator.current_kind = "constructor"
                    elif value_stack[-2].val == "function":
                        self.generator.current_kind = "function"
                i += 1
            elif action.startswith("R"):
                rule_idx = int(action[1:])
                rule = self.rules[rule_idx]

                args = []
                for _ in range(
                        len(rule.right)
                ):  # TODO: check panic when value_stack/stack empty
                    stack.pop()
                    args.append(value_stack.pop())
                args.reverse()

                result = self.generator.generate(rule, args)

                state_before = stack[-1]
                goto_state = self.goto_table.get((state_before, rule.left))
                stack.append(goto_state)
                value_stack.append(result)
            elif action == "ACC":
                return True
            else:
                raise ERR_UNEXPECTED_STATE

    def tokenize_and_parse(self, text):
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()
        if not tokens:
            return False
        return self.run_parser(tokens)

    def precompile(self, table, text):
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()
        if not tokens:
            return False

        pos = 0
        # Ожидаем 'class' ClassName '{'
        if tokens[pos].val != "class":
            return False
        pos += 1
        if pos >= len(tokens):
            return False
        class_name = tokens[pos].val
        pos += 1
        if tokens[pos].val != "{":
            return False
        pos += 1

        while pos < len(tokens):
            token = tokens[pos]
            if token.val not in ("constructor", "function", "method"):
                pos += 1
                continue
            kind_str = token.val
            if kind_str == "constructor":
                kind = SubroutineKind.constructor
            elif kind_str == "function":
                kind = SubroutineKind.function
            else:
                kind = SubroutineKind.method
            pos += 1
            if pos >= len(tokens):
                return False
            return_type = tokens[pos].val
            pos += 1
            if pos >= len(tokens):
                return False
            sub_name = tokens[pos].val
            pos += 1
            if tokens[pos].val != "(":
                return False
            pos += 1

            n_params = 0
            stacked = 1
            if tokens[pos].val != ")":
                n_params = 1
                while stacked:
                    if pos >= len(tokens):
                        return False
                    if tokens[pos].val == "," and stacked == 1:
                        n_params += 1
                    elif tokens[pos].val == "(":
                        stacked += 1
                    elif tokens[pos].val == ")":
                        stacked -= 1
                    pos += 1
            pos += 1
            if pos >= len(tokens):
                return False
            sub = Subroutine(
                class_name=class_name,
                sub_name=sub_name,
                kind=kind,
                params_count=n_params,
                res_type=return_type,
            )
            table[sub.get_full_name()] = sub

        return True

    def parse(self, text, func_table):
        self.generator = CodeGenerator(func_table, self.label_index)
        res = self.tokenize_and_parse(text)
        self.label_index = self.generator.label_idx
        return (
            res,
            self.generator.vm.get_collected(),
        self.generator.class_name,
        )  # TODO: check generator's vm
