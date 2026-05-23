from compiler.source.code_generator.vm_writer import VMWriter
from compiler.source.errors.code_generator_errors import (
    ErrUnknownFunc,
    ErrUnknownSymbol,
)
from compiler.source.tokenizer.token_type import TokenType
from compiler.source.code_generator.symbol_table import SymbolKind, SymbolTable
from compiler.source.code_generator.non_terminal import (
    NonTerminal,
    NTwithCode,
    NTTitle,
    NTwithVarList,
    NTwithTypedVarList,
    Token,
)
from compiler.source.code_generator.var_types import VarTypes
from compiler.source.precompile.subroutine_kind import SubroutineKind


class CodeGenerator:
    """Класс генератора кода. Записывает вм команды в зависимости от нетерминала

    Аргументы:
    - func_table: таблица функций найденных на этапе прекомпиляции
    - label_idx: индексация лейблов должна сохранятьося между несколькими файлами
    """

    def __init__(self, func_table, label_idx):
        self.class_name = ""
        self.current_kind = None
        self.label_idx = label_idx
        self.symbols = SymbolTable()
        self.vm = VMWriter()
        self.subroutine_table = func_table
        self.handler_map = None
        self.init_map()

    def get_collected(self):
        """Вернуть список команд виртуальной машины"""
        return self.vm.get_collected()

    def init_map(self):
        """Обработчики нетерминалов"""
        self.handler_map = {
            NTTitle.S: self.handle_s,
            NTTitle.ClassVarDecList: self.handle_class_var_dec_list,
            NTTitle.SubroutineDecList: self.handle_subroutine_dec_list,
            NTTitle.ClassVarDec: self.handle_class_var_dec,
            NTTitle.Type: self.handle_type,
            NTTitle.VarNameList: self.handle_var_name_list,
            NTTitle.VarName: self.handle_var_name,
            NTTitle.ClassName: self.handle_class_name,
            NTTitle.SubroutineName: self.handle_subroutine_name,
            NTTitle.SubroutineDec: self.handle_subroutine_dec,
            NTTitle.ParameterList: self.handle_parametr_list,
            NTTitle.TypedVarNameList: self.handle_typed_var_name_list,
            NTTitle.SubroutineBody: self.handle_subroutine_body,
            NTTitle.VarDeclarationList: self.handle_var_declaration_list,
            NTTitle.VarDeclaration: self.handle_var_declaration,
            NTTitle.StatementsList: self.handle_statements_list,
            NTTitle.Statement: self.handle_statement,
            NTTitle.LetStatement: self.handle_let_statement,
            NTTitle.IfStatement: self.handle_if_statement,
            NTTitle.IfHeader: self.handle_if_header,
            NTTitle.ElsePart: self.handle_else_part,
            NTTitle.WhileHeader: self.handle_while_header,
            NTTitle.WhileStatement: self.handle_while_statement,
            NTTitle.DoStatement: self.handle_do_statement,
            NTTitle.ReturnStatement: self.handle_return_statement,
            NTTitle.Expression: self.handle_expression,
            NTTitle.UnaryOperationList: self.handle_unary_operation_list,
            NTTitle.Term: self.handle_term,
            NTTitle.SubroutineCall: self.handle_subroutine_call,
            NTTitle.ExpressionList: self.handle_expression_list,
            NTTitle.KeywordConstant: self.handle_keyword,
            NTTitle.UnaryOperation: self.handle_unary_operation,
            NTTitle.Operation: self.handle_operation,
            NTTitle.ReturnType: self.handle_return_type,
        }

    # S -> 'class' ClassName '{' ClassVarDecList SubroutineDecList '}'
    # S -> 'class' ClassName '{' ClassVarDecList '}'
    # S -> 'class' ClassName '{' SubroutineDecList '}'
    # S -> 'class' ClassName '{' '}'
    def handle_s(self, args):
        for arg in args:
            if isinstance(arg, NTwithCode) and arg.title == NTTitle.SubroutineDecList:
                self.vm.output = arg.vm.get_collected()
        return NonTerminal(NTTitle.S, self._get_start_token(args[0]), "S")

    # ClassVarDecList -> ClassVarDec
    # ClassVarDecList -> ClassVarDecList ClassVarDec
    def handle_class_var_dec_list(self, args):
        return NonTerminal(NTTitle.ClassVarDecList, self._get_start_token(args[0]))

    # ClassVarDec -> 'static' Type VarNameList ';'
    # ClassVarDec -> 'field' Type VarNameList ';'
    def handle_class_var_dec(self, args):
        kind = SymbolKind.STATIC if args[0].val == "static" else SymbolKind.FIELD
        v_type = args[1].val
        for name in args[2].get_var_list():
            self.symbols.define(name, v_type, kind)
        return NTwithVarList(
            NTTitle.ClassVarDec,
            self._get_start_token(args[0]),
            v_type,
            var_list=args[2].get_var_list(),
        )

    # VarNameList -> VarName
    # VarNameList -> VarNameList ',' VarName
    def handle_var_name_list(self, args):
        if len(args) == 1:
            return NTwithVarList(
                NTTitle.VarNameList,
                self._get_start_token(args[0]),
                VarTypes.unknown,
                var_list=[args[0].val],
            )
        args[0].var_list.append(args[2].val)
        return args[0]

    # Type -> 'int'
    # Type -> 'char'
    # Type -> 'boolean'
    # Type -> ClassName
    def handle_type(self, args):
        if not isinstance(args[0], Token):
            return NonTerminal(
                NTTitle.Type,
                self._get_start_token(args[0]),
                args[0].val,  # Save ClassName
            )
        return NonTerminal(
            NTTitle.Type,
            self._get_start_token(args[0]),
            VarTypes[args[0].val],  # Save
        )

    # TypedVarNameList -> Type VarName
    # TypedVarNameList -> TypedVarNameList ',' Type VarName
    def handle_typed_var_name_list(self, args):
        if len(args) == 2:
            return NTwithTypedVarList(
                NTTitle.TypedVarNameList,
                self._get_start_token(args[0]),
                typed_var_list=[(args[0].val, args[1].val)],
            )
        args[0].typed_var_list.append((args[2].val, args[3].val))
        return args[0]

    # ParameterList -> '(' ')'
    # ParameterList -> '(' TypedVarNameList ')'
    def handle_parametr_list(self, args):
        if self.current_kind == "method":
            self.symbols.define("this", VarTypes.className, SymbolKind.ARG)
        if len(args) == 2:
            return NonTerminal(NTTitle.ParameterList, self._get_start_token(args[0]))
        for p_type, p_name in args[1].get_typed_var_list():
            self.symbols.define(p_name, p_type, SymbolKind.ARG)
        return NonTerminal(NTTitle.ParameterList, self._get_start_token(args[0]))

    # SubroutineDecList -> SubroutineDec
    # SubroutineDecList -> SubroutineDecList SubroutineDec
    def handle_subroutine_dec_list(self, args):
        writable = NTwithCode(NTTitle.SubroutineDecList, self._get_start_token(args[0]))
        for sub in args:
            writable.extend(sub.vm)
        return writable

    # VarDeclaration -> 'var' Type VarNameList ';'
    def handle_var_declaration(self, args):
        v_type = args[1].val
        for name in args[2].get_var_list():
            self.symbols.define(name, v_type, SymbolKind.VAR)
        return NTwithVarList(
            NTTitle.VarDeclaration,
            self._get_start_token(args[0]),
            v_type,
            var_list=args[2].get_var_list(),
        )

    # VarDeclarationList -> VarDeclaration
    # VarDeclarationList -> VarDeclarationList VarDeclaration
    def handle_var_declaration_list(self, args):
        return NonTerminal(NTTitle.VarDeclarationList, self._get_start_token(args[0]))

    # SubroutineBody -> '{' VarDeclarationList StatementsList '}'
    # SubroutineBody -> '{' VarDeclarationList '}'
    # SubroutineBody -> '{' StatementsList '}'
    # SubroutineBody -> '{' '}'
    def handle_subroutine_body(self, args):
        writable = NTwithCode(NTTitle.SubroutineBody, self._get_start_token(args[0]))
        for arg in args:
            if isinstance(arg, NTwithCode) and arg.title == NTTitle.StatementsList:
                writable.extend(arg.vm)
        return writable

    # ReturnType -> Type
    # ReturnType -> 'void'
    def handle_return_type(self, args):
        if isinstance(args[0], Token):
            val = "void"
        else:
            val = args[0].val
        return NonTerminal(NTTitle.ReturnType, self._get_start_token(args[0]), val)

    # SubroutineDec -> 'constructor' ClassName SubroutineName ParameterList SubroutineBody
    # SubroutineDec -> 'function' ReturnType SubroutineName ParameterList SubroutineBody
    # SubroutineDec -> 'method' ReturnType SubroutineName ParameterList SubroutineBody
    def handle_subroutine_dec(self, args):
        writable = NTwithCode(NTTitle.SubroutineDec, self._get_start_token(args[0]))
        s_kind = args[0].val
        # ret_type = args[1].val # TODO: type checking
        s_name = args[2].val
        n_locals = self.symbols.var_count(SymbolKind.VAR)
        writable.vm.write_function(f"{self.class_name}.{s_name}", n_locals)

        if s_kind == "constructor":
            n_fields = self.symbols.var_count(SymbolKind.FIELD)
            writable.vm.write_push("constant", n_fields)
            writable.vm.write_call("Memory.alloc", 1)
            writable.vm.write_pop("pointer", 0)
        elif s_kind == "method":
            writable.vm.write_push("argument", 0)
            writable.vm.write_pop("pointer", 0)

        writable.extend(args[4].vm)
        self.symbols.start_subroutine()
        return writable

    # LetStatement -> 'let' VarName '=' Expression ';'
    # LetStatement -> 'let' VarName '[' Expression ']' '=' Expression ';'
    def handle_let_statement(self, args):
        writable = NTwithCode(NTTitle.LetStatement, self._get_start_token(args[0]))
        var, ok = self.symbols[args[1]]
        if not ok:
            raise ErrUnknownSymbol(*args[1].start_token.get_pos())
        if len(args) == 5:  # let VarName = Expression ;
            writable.extend(args[3].vm)
            writable.vm.write_pop(var.kind, var.index)
        else:  # let VarName [ Expression ] = Expression ;
            var, ok = self.symbols[args[1]]
            if not ok:
                raise ErrUnknownSymbol(*args[1].start_token.get_pos())
            writable.vm.write_push(var.kind, var.index)
            writable.extend(args[3].vm)
            writable.vm.write_arithmetic("add")
            writable.vm.write_pop("temp", 0)
            writable.extend(args[6].vm)
            writable.vm.write_push("temp", 0)
            writable.vm.write_pop("pointer", 1)
            writable.vm.write_pop("that", 0)
        return writable

    # ReturnStatement -> 'return' ';'
    # ReturnStatement -> 'return' Expression ';'
    def handle_return_statement(self, args):
        writable = NTwithCode(NTTitle.ReturnStatement, self._get_start_token(args[0]))
        if len(args) == 2:
            writable.vm.write_push("constant", 0)
        else:
            writable.extend(args[1].vm)
        writable.vm.write_return()
        return writable

    # DoStatement -> 'do' SubroutineCall ';'
    def handle_do_statement(self, args):
        writable = NTwithCode(NTTitle.DoStatement, self._get_start_token(args[0]))
        writable.extend(args[1].vm)
        writable.vm.write_pop("temp", 0)
        return writable

    # Expression -> Term
    # Expression -> UnaryOperationList Term
    # Expression -> Expression Operation Term
    # Expression -> Expression Operation UnaryOperationList Term
    def handle_expression(self, args):
        writable = NTwithCode(NTTitle.Expression, self._get_start_token(args[0]))
        if len(args) == 1:
            writable.extend(args[0].vm)  # Term
        if len(args) == 2:
            writable.extend(args[1].vm)  # Term
            writable.extend(args[0].vm)  # UnaryOperationList
        if len(args) == 3:
            writable.extend(args[0].vm)  # Expression
            writable.extend(args[2].vm)  # Term
            writable.extend(args[1].vm)  # Operation
        if len(args) == 4:
            writable.extend(args[0].vm)  # Expression
            writable.extend(args[3].vm)  # Term
            writable.extend(args[2].vm)  # UnaryOperationList
            writable.extend(args[1].vm)  # Operation
        return writable

    # SubroutineCall -> SubroutineName '(' ')'
    # SubroutineCall -> SubroutineName '(' ExpressionList ')'
    # SubroutineCall -> VarName '.' SubroutineName '(' ')'
    # SubroutineCall -> VarName '.' SubroutineName '(' ExpressionList ')'
    def handle_subroutine_call(self, args):
        writable = NTwithCode(NTTitle.SubroutineCall, self._get_start_token(args[0]))
        if len(args) < 5:
            sub_name = args[0].val
            class_name = self.class_name
            full_name = f"{class_name}.{sub_name}"
            sig = self.subroutine_table.get(full_name)
            if sig is None:
                raise ErrUnknownFunc(full_name)
            if sig.kind == SubroutineKind.method:
                writable.vm.write_push("pointer", 0)
            if len(args) == 4:  # SubroutineName '(' ExpressionList ')'
                writable.extend(args[2].vm)
            writable.vm.write_call(full_name, sig.get_nargs())

        else:
            sub_name = args[2].val
            name = args[0].val
            var, ok = self.symbols[args[0]]  # VarName | ClassName
            if ok:
                full_name = f"{var.var_type}.{sub_name}"
                sig = self.subroutine_table.get(full_name)
                if sig is None:
                    raise ErrUnknownFunc(full_name)
                writable.vm.write_push(var.kind, var.index)
            else:
                full_name = f"{name}.{sub_name}"
                sig = self.subroutine_table.get(full_name)
                if sig is None:
                    raise ErrUnknownFunc(full_name)

            if len(args) == 6:  # VarName '.' SubroutineName '(' ExpressionList ')'
                writable.extend(args[4].vm)

            writable.vm.write_call(full_name, sig.get_nargs())
        return writable

    # ExpressionList -> Expression
    # ExpressionList -> ExpressionList ',' Expression
    def handle_expression_list(self, args):
        writable = NTwithCode(NTTitle.ExpressionList, self._get_start_token(args[0]))
        writable.extend(args[0].vm)
        if len(args) == 3:
            writable.extend(args[2].vm)
        return writable

    # UnaryOperationList -> UnaryOperation
    # UnaryOperationList -> UnaryOperationList UnaryOperation
    def handle_unary_operation_list(self, args):
        writable = NTwithCode(
            NTTitle.UnaryOperationList, self._get_start_token(args[0])
        )
        writable.extend(args[0].vm)
        if len(args) == 2:
            writable.extend(args[1].vm)
        return writable

    # UnaryOperation -> '-'
    # UnaryOperation -> '~'
    def handle_unary_operation(self, args):
        writable = NTwithCode(NTTitle.UnaryOperation, self._get_start_token(args[0]))
        writable.vm.write_arithmetic({"-": "neg", "~": "not"}[args[0].val])
        return writable

    # Operation -> Token()...
    def handle_operation(self, args):
        writable = NTwithCode(NTTitle.Operation, self._get_start_token(args[0]))
        self._write_op_to_writer(args[0].val, writable.vm)
        return writable

    # IfHeader -> 'if' '(' Expression ')'
    def handle_if_header(self, args):
        idx = self.label_idx
        self.label_idx += 2
        writable = NTwithCode(
            NTTitle.IfHeader,
            self._get_start_token(args[0]),
            ifl1=f"IF_{idx}",
            ifl2=f"IF_{idx + 1}",
        )
        writable.extend(args[2].vm)
        writable.vm.write_arithmetic("not")
        writable.vm.write_if(writable.kwargs["ifl1"])
        return writable

    # ElsePart -> 'else' '{' StatementsList '}'
    # ElsePart -> 'else' '{' '}'
    def handle_else_part(self, args):
        writable = NTwithCode(NTTitle.ElsePart, self._get_start_token(args[0]))
        if len(args) == 4:
            writable.extend(args[2].vm)
        return writable

    # IfStatement -> IfHeader '{' StatementsList '}'
    # IfStatement -> IfHeader '{' StatementsList '}' ElsePart
    # IfStatement -> IfHeader '{' '}'
    # IfStatement -> IfHeader '{' '}' ElsePart
    def handle_if_statement(self, args):
        writable = NTwithCode(
            NTTitle.IfStatement, self._get_start_token(args[0]), **args[0].kwargs
        )
        writable.extend(args[0].vm)
        if args[2].val != "}":
            writable.extend(args[2].vm)
        writable.vm.write_goto(writable.kwargs["ifl2"])
        writable.vm.write_label(writable.kwargs["ifl1"])
        if not isinstance(args[-1], Token):
            writable.extend(args[-1].vm)
        writable.vm.write_label(writable.kwargs["ifl2"])
        return writable

    # WhileHeader -> 'while' '(' Expression ')'
    def handle_while_header(self, args):
        idx = self.label_idx
        self.label_idx += 2
        writable = NTwithCode(
            NTTitle.WhileHeader,
            self._get_start_token(args[0]),
            l1=f"WHILE_EXP{idx}",
            l2=f"WHILE_EXP{idx + 1}",
        )
        writable.vm.write_label(writable.kwargs["l1"])
        writable.extend(args[2].vm)
        writable.vm.write_arithmetic("not")
        writable.vm.write_if(writable.kwargs["l2"])
        return writable

    # WhileStatement -> WhileCondition '{' StatementsList '}'
    # WhileStatement -> WhileCondition '{' '}'
    def handle_while_statement(self, args):
        writable = NTwithCode(
            NTTitle.WhileStatement, self._get_start_token(args[0]), **args[0].kwargs
        )
        writable.extend(args[0].vm)
        if len(args) == 4:
            writable.extend(args[2].vm)
        writable.vm.write_goto(writable.kwargs["l1"])
        writable.vm.write_label(writable.kwargs["l2"])
        return writable

    # StatementsList -> Statement
    # StatementsList -> StatementsList Statement
    def handle_statements_list(self, args):
        writable = NTwithCode(NTTitle.StatementsList, self._get_start_token(args[0]))
        writable.extend(args[0].vm)
        if len(args) == 2:
            writable.extend(args[1].vm)
        return writable

    # Statement -> LetStatement
    # Statement -> IfStatement
    # Statement -> WhileStatement
    # Statement -> DoStatement
    # Statement -> ReturnStatement
    def handle_statement(self, args):
        writable = NTwithCode(NTTitle.Statement, self._get_start_token(args[0]))
        writable.extend(args[0].vm)
        return writable

    # KeywordConstant -> 'true'
    # KeywordConstant -> 'false'
    # KeywordConstant -> 'null'
    # KeywordConstant -> 'this'
    def handle_keyword(self, args):
        writable = NTwithCode(NTTitle.KeywordConstant, self._get_start_token(args[0]))
        if args[0].val == "null" or args[0].val == "false":
            writable.vm.write_push("constant", 0)
        elif args[0].val == "true":
            writable.vm.write_push("constant", 1)
            writable.vm.write_arithmetic("neg")
        else:
            writable.vm.write_push("pointer", 0)
        return writable

    # Term -> integerConstant
    # Term -> stringConstant
    # Term -> KeywordConstant
    # Term -> VarName
    # Term -> VarName '[' Expression ']'
    # Term -> '(' Expression ')'
    # Term -> SubroutineCall
    def handle_term(self, args):
        writable = NTwithCode(NTTitle.Term, self._get_start_token(args[0]))
        if isinstance(args[0], Token):
            val = args[0]
            if val.token_type == TokenType.integerConstant:
                writable.vm.write_push("constant", val.val)
            elif val.token_type == TokenType.stringConstant:
                s = val.val
                writable.vm.write_push("constant", len(s))
                writable.vm.write_call("String.new", 1)
                for ch in s:
                    writable.vm.write_push("constant", ord(ch))
                    writable.vm.write_call("String.appendChar", 2)
            elif len(args) == 3:
                writable.extend(args[1].vm)
        elif len(args) == 4:
            var, ok = self.symbols[args[0]]
            if not ok:
                raise ErrUnknownSymbol(*args[0].start_token.get_pos())
            writable.vm.write_push(var.kind, var.index)
            writable.extend(args[2].vm)  # Expression
            writable.vm.write_arithmetic("add")
            writable.vm.write_pop("pointer", 1)
            writable.vm.write_push("that", 0)
        elif args[0].title == NTTitle.VarName:
            var, ok = self.symbols[args[0]]
            if not ok:
                raise ErrUnknownSymbol(*args[0].start_token.get_pos())
            writable.vm.write_push(var.kind, var.index)
        elif (
            args[0].title == NTTitle.SubroutineCall
            or args[0].title == NTTitle.KeywordConstant
        ):
            writable.extend(args[0].vm)
        return writable

    # VarName -> identifier
    def handle_var_name(self, args):
        return NonTerminal(NTTitle.VarName, self._get_start_token(args[0]), args[0].val)

    # SubroutineName -> identifier
    def handle_subroutine_name(self, args):
        return NonTerminal(
            NTTitle.SubroutineName, self._get_start_token(args[0]), args[0].val
        )

    # ClassName -> identifier
    def handle_class_name(self, args):
        return NonTerminal(
            NTTitle.ClassName, self._get_start_token(args[0]), args[0].val
        )

    def generate(self, rule, args):
        lhs = rule.left

        if lhs == NTTitle.ClassName and not self.class_name:
            self.class_name = args[0].val

        return self.handler_map[lhs](args)

    def _write_op_to_writer(self, op, writer):  # TODO: type checking
        ops = {
            "+": "add",
            "-": "sub",
            "*": "call Math.multiply 2",
            "/": "call Math.divide 2",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq",
        }
        cmd = ops[op]
        if cmd.startswith("call"):
            writer.output.append(cmd)
        else:
            writer.write_arithmetic(cmd)

    @staticmethod
    def _get_start_token(arg):
        if isinstance(arg, Token):
            return arg
        return arg.start_token
