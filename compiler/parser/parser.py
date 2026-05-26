import csv
from typing import Optional

from compiler.errors.parser_errors import ERR_UNEXPECTED_STATE, ErrorUnexpectedGoToState
from compiler.code_generator.code_generator import CodeGenerator, HANDLER_TYPE
from compiler.tokenizer.tokenizer import Tokenizer, TokenType, Token
from compiler.grammar.grammar_reader import GrammarReader
from compiler.precompile.subroutine import SubroutineKind, Subroutine


class Parser:
    """Класс парсера. Координирует действия остальных модулей,
     а также выполняет свертки

    Аргументы:
    - grammar_file: Путь до файла грамматики
    - states_file: Путь  до файла таблицы slr анализатора
    """

    def __init__(self, grammar_file: str, states_file: str) -> None:
        self.reader = GrammarReader(grammar_file)
        self.rules = self.reader.rules
        self.action_table: dict[tuple[int, str], str] = {}
        self.goto_table: dict[tuple[int, str], int] = {}
        self._load_table(states_file)
        self.generator: Optional[CodeGenerator] = None
        self.label_index = 0

    def _load_table(self, path: str) -> None:
        """Загрузка таблицы slr анализатора"""
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"Internal Error: File {path} not found or incorrect format")
                return
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

    @staticmethod
    def _get_lookahead(token: Token) -> str:
        """Вернуть нужное значение из токена"""
        if token.token_type in (TokenType.keyword, TokenType.symbol):
            return token.val
        return token.token_type.name

    def _run_parser(self, tokens: list[Token]) -> bool:
        if not isinstance(self.generator, CodeGenerator):
            print("Internal Error: Code generator is not initialized")
            return False
        """Основная рабоиа с анализатором и генерация кода"""
        tokens.append(Token(TokenType.EOF, "EOF"))
        stack = [0]
        value_stack: HANDLER_TYPE = []

        i = 0
        while True:
            state = stack[-1]
            token = tokens[i]
            lookahead = self._get_lookahead(token)

            action = self.action_table.get((state, lookahead))
            if not action:
                print(
                    f"Syntax Error at row {token.row}, col {token.col}: Unexpected token '{token.val}'"
                )
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
                for _ in range(len(rule.right)):
                    stack.pop()
                    args.append(value_stack.pop())
                args.reverse()

                try:
                    result = self.generator.generate(rule, args)
                except Exception as e:
                    print(f"ERROR: {e}\n\nAborting...")
                    return False
                state_before = stack[-1]
                goto_state = self.goto_table.get((state_before, rule.left))
                if goto_state is None:
                    raise ErrorUnexpectedGoToState(state_before, rule.left)
                stack.append(goto_state)
                value_stack.append(result)
            elif action == "ACC":
                return True
            else:
                raise ERR_UNEXPECTED_STATE

    def tokenize_and_parse(self, text: str) -> bool:
        """Запуск токенайзера, токенизация перед запуском кодогенерации"""
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()
        if not tokens:
            return False
        return self._run_parser(tokens)

    @staticmethod
    def precompile(table, text: str) -> bool:
        """Токенипзация и поиск сигнатур всех функций"""
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

    def parse(
        self, text: str, func_table: dict[str, Subroutine]
    ) -> tuple[bool, list[str], str]:
        """Полный парсинг кода. Возвращает корректен ли файл, список vm команд, имя класса"""
        self.generator = CodeGenerator(func_table, self.label_index)
        res = self.tokenize_and_parse(text)
        self.label_index = self.generator.label_idx
        return (
            res,
            self.generator.vm.get_collected,
            self.generator.class_name,
        )
