import csv

from code_generator.symbol_table import SymbolTable, SymbolKind
from code_generator.vm_writer import VMWriter
from tokenizer.tokenizer import Tokenizer
from tokenizer.token_type import TokenType
from tokenizer.token import Token
from grammar.grammar_reader import GrammarReader
from parser.parser_tools import *


class Parser:
    def __init__(self, table_path="cmplr/source/grammar/jack_slr_table.csv",
                 grammar_path="cmplr/source/grammar/grammar"):
        self.reader = GrammarReader(grammar_path)
        self.rules = self.reader.rules
        self.action_table = {}
        self.goto_table = {}
        self._load_table(table_path)

        self.symbols = SymbolTable()
        self.vm = VMWriter()
        self.class_name = ""
        self.label_idx = 0
        self.collected_vm = []

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

    def _val(self, arg):
        if isinstance(arg, Token):
            return arg.value
        return arg

    def _get_lookahead(self, token):
        if token.TokenType in (TokenType.keyword, TokenType.symbol):
            return token.value
        return token.TokenType.name

    def run_parser(self, tokens):
        tokens.append(Token(None, "$"))
        stack = [0]
        value_stack = []

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
                value_stack.append(token)
                i += 1
            elif action.startswith('R'):
                rule_idx = int(action[1:])
                rule = self.rules[rule_idx]

                args = []
                for _ in range(len(rule.right)):
                    stack.pop()
                    args.append(value_stack.pop())
                args.reverse()

                result = self.generate_code(rule, args)

                state_before = stack[-1]
                goto_state = self.goto_table.get((state_before, rule.left))
                stack.append(goto_state)
                value_stack.append(result)
            elif action == 'ACC':
                print("Parsing and Code Generation Successful!")
                return True

    def generate_code(self, rule, args):
        lhs = rule.left

        if lhs == "ClassName":
            if not self.class_name:
                self.class_name = self._val(args[0])
                # print(f"  [DEBUG] Class defined: {self.class_name}")
            return self._val(args[0])

        if lhs in ["VarName", "SubroutineName", "Type", "Operation", "UnaryOperation", "KeywordConstant"]:
            return self._val(args[0])

        if lhs == "VarNameList":
            if len(args) == 1: return [self._val(args[0])]
            return args[0] + [self._val(args[2])]

        if lhs == "TypedVarNameList":
            if len(args) == 2:
                return [(self._val(args[0]), self._val(args[1]))]
            return args[0] + [(self._val(args[2]), self._val(args[3]))]

        if lhs == "ParameterList":
            params = args[1] if len(args) == 3 else []
            for p_type, p_name in params:
                self.symbols.define(p_name, p_type, SymbolKind.ARG)
            return params

        if lhs == "ClassVarDec":
            kind = SymbolKind.STATIC if self._val(args[0]) == "static" else SymbolKind.FIELD
            v_type = self._val(args[1])
            for name in args[2]:
                self.symbols.define(name, v_type, kind)
            return None

        if lhs == "VarDeclaration":
            v_type = self._val(args[1])
            for name in args[2]:
                self.symbols.define(name, v_type, SymbolKind.VAR)
            return None

        if lhs == "SubroutineDec":
            s_kind = self._val(args[0])
            s_name = self._val(args[2])
            n_locals = self.symbols.var_count(SymbolKind.VAR)

            header = [f"function {self.class_name}.{s_name} {n_locals}"]

            if s_kind == "constructor":
                n_fields = self.symbols.var_count(SymbolKind.FIELD)
                header.append(f"push constant {n_fields}")
                header.append("call Memory.alloc 1")
                header.append("pop pointer 0")
            elif s_kind == "method":
                self._patch_method_arguments()
                header.append("push argument 0")
                header.append("pop pointer 0")

            self.vm.output = header + self.vm.output
            self.collected_vm.extend(self.vm.output)

            self.vm.output = []
            self.symbols.start_subroutine()
            return None

        if lhs == "LetStatement":
            if len(args) == 5:  # let VarName = Expression ;
                var_name = self._val(args[1])
                kind = self.symbols.kind_of(var_name)
                idx = self.symbols.index_of(var_name)
                self.vm.write_pop("temp", 0)
                self.vm.write_push("temp", 0)
                self.vm.write_pop(kind, idx)
            else:  # let VarName [ Expression ] = Expression ;
                var_name = self._val(args[1])
                kind = self.symbols.kind_of(var_name)
                v_idx = self.symbols.index_of(var_name)
                self.vm.write_pop("temp", 0)   # value
                self.vm.write_pop("temp", 1)   # index
                self.vm.write_push(kind, v_idx)
                self.vm.write_push("temp", 1)
                self.vm.write_arithmetic("add")
                self.vm.write_pop("pointer", 1)
                self.vm.write_push("temp", 0)
                self.vm.write_pop("that", 0)
            return None

        if lhs == "DoStatement":
            self.vm.write_pop("temp", 0)
            return None

        if lhs == "ReturnStatement":
            if len(args) == 2:
                self.vm.write_push("constant", 0)
            self.vm.write_return()
            return None

        if lhs == "Expression":
            if len(args) == 3:
                self._write_op(self._val(args[1]))
            elif len(args) == 2:
                for op in reversed(self._get_unary_list(args[0])):
                    self.vm.write_arithmetic("neg" if op == '-' else "not")
            elif len(args) == 4:
                self._write_op(self._val(args[1]))
                for op in reversed(self._get_unary_list(args[2])):
                    self.vm.write_arithmetic("neg" if op == '-' else "not")
            return None

        if lhs == "Term":
            if len(args) == 1:
                self._handle_term(args[0])
            elif len(args) == 4:
                self._handle_array_term(args)
            return None

        if lhs == "SubroutineCall":
            self._handle_call(args)
            return None

        if lhs == "ExpressionList":
            return (args[0] + 1) if len(args) > 1 else (1 if len(args) == 1 else 0)

        if lhs == "UnaryOperationList":
            if len(args) == 1:
                return [self._val(args[0])]
            return [self._val(args[0])] + (args[1] if isinstance(args[1], list) else [args[1]])

        if lhs == "IfHeader":
            idx = self.label_idx
            self.label_idx += 1
            self.vm.write_if(f"IF_TRUE{idx}")
            self.vm.write_goto(f"IF_FALSE{idx}")
            self.vm.write_label(f"IF_TRUE{idx}")
            return idx

        if lhs == "IfStatement":
            idx = args[0]
            self.vm.write_label(f"IF_FALSE{idx}")
            if len(args) >= 4:
                end_idx = self.label_idx
                self.label_idx += 1
                self.vm.write_goto(f"IF_END{end_idx}")
                self.vm.write_label(f"IF_END{end_idx}")
            return None

        if lhs == "WhileHeader":
            idx = self.label_idx
            self.label_idx += 1
            self.vm.write_label(f"WHILE_EXP{idx}")
            return idx

        if lhs == "WhileCondition":
            idx = args[0]
            self.vm.write_arithmetic("not")
            self.vm.write_if(f"WHILE_END{idx}")
            return idx

        if lhs == "WhileStatement":
            idx = args[0]
            self.vm.write_goto(f"WHILE_EXP{idx}")
            self.vm.write_label(f"WHILE_END{idx}")
            return None

        if lhs == "S":
            if not self.class_name and len(args) > 1:
                self.class_name = self._val(args[1])
            return None

        return None

    def _handle_term(self, val):
        if isinstance(val, Token):
            if val.TokenType == TokenType.integerConstant:
                self.vm.write_push("constant", val.value)
            elif val.TokenType == TokenType.stringConstant:
                s = val.value
                self.vm.write_push("constant", len(s))
                self.vm.write_call("String.new", 1)
                for ch in s:
                    self.vm.write_push("constant", ord(ch))
                    self.vm.write_call("String.appendChar", 2)
        else:
            if val == "this":
                self.vm.write_push("pointer", 0)
            elif val == "true":
                self.vm.write_push("constant", 0)
                self.vm.write_arithmetic("not")
            elif val in ("false", "null"):
                self.vm.write_push("constant", 0)
            else:
                kind = self.symbols.kind_of(val)
                idx = self.symbols.index_of(val)
                self.vm.write_push(kind, idx)

    def _handle_array_term(self, args):
        var_name = self._val(args[0])
        kind = self.symbols.kind_of(var_name)
        v_idx = self.symbols.index_of(var_name)
        self.vm.write_pop("temp", 1)
        self.vm.write_push(kind, v_idx)
        self.vm.write_push("temp", 1)
        self.vm.write_arithmetic("add")
        self.vm.write_pop("pointer", 1)
        self.vm.write_push("that", 0)

    def _handle_call(self, args):
        if len(args) in (3, 4):
            name = self._val(args[0])
            n_args = args[2] if len(args) == 4 and isinstance(args[2], int) else 0
            self.vm.write_push("pointer", 0)
            self.vm.write_call(f"{self.class_name}.{name}", n_args + 1)
            return

        if len(args) in (5, 6):
            target = self._val(args[0])
            sub_name = self._val(args[2])
            n_args = args[4] if len(args) == 6 and isinstance(args[4], int) else 0

            kind = self.symbols.kind_of(target)
            if kind != SymbolKind.NONE:
                v_type = self.symbols.type_of(target)
                idx = self.symbols.index_of(target)
                self.vm.write_push(kind, idx)
                self.vm.write_call(f"{v_type}.{sub_name}", n_args + 1)
            else:
                self.vm.write_call(f"{target}.{sub_name}", n_args)

    def _write_op(self, op):
        ops = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2',
               '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}
        cmd = ops[op]
        if cmd.startswith('call'):
            self.vm.output.append(cmd)
        else:
            self.vm.write_arithmetic(cmd)

    def _get_unary_list(self, val):
        if isinstance(val, list):
            return val
        return [val] if val else []

    def _patch_method_arguments(self):
        new_out = []
        for line in self.vm.output:
            if "argument" in line:
                parts = line.split()
                if len(parts) == 3 and parts[1] == "argument":
                    new_out.append(f"{parts[0]} argument {int(parts[2]) + 1}")
                    continue
            new_out.append(line)
        self.vm.output = new_out

    def tokenize_and_parse(self, file_path):
        text = open_file(file_path)
        tokenizer = Tokenizer(text)
        tokens = tokenizer.tokenize()
        if not tokens:
            return False
        return self.run_parser(tokens)

    def parse_all(self, files):
        for file in files:
            print(f"\n--- Processing {file} ---")
            self.vm = VMWriter()
            self.symbols = SymbolTable()
            self.label_idx = 0
            self.collected_vm = []
            self.class_name = ""

            success = self.tokenize_and_parse(file)

            if success:
                self.save_vm_file(file)
                print(f"--- File {file}: success ---")
            else:
                print(f"--- File {file} FAILED ---")

    def save_vm_file(self, jack_file_path):
        vm_file_path = jack_file_path.replace(".jack", ".vm")
        with open(vm_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.collected_vm) + "\n")
        self.collected_vm = []