from compiler.source.code_generator.vm_writer import VMWriter
from compiler.source.errors.code_generator_errors import ErrUnknownFunc
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
    def __init__(self, func_table):
        self.class_name = ""
        self.label_idx = 0
        self.symbols = SymbolTable()
        self.vm = VMWriter()
        self.subroutine_table = func_table

    def get_collected(self):
        return self.vm.get_collected()

    def generate(self, rule, args):
        lhs = rule.left

        # S -> 'class' ClassName '{' ClassVarDecList SubroutineDecList '}'
        # S -> 'class' ClassName '{' ClassVarDecList '}'
        # S -> 'class' ClassName '{' SubroutineDecList '}'
        # S -> 'class' ClassName '{' '}'
        if lhs == NTTitle.S:
            for arg in args:
                if (
                    isinstance(arg, NTwithCode)
                    and arg.title == NTTitle.SubroutineDecList
                ):
                    self.vm.output = arg.vm.get_collected()
            return NonTerminal(NTTitle.S, self._get_start_token(args[0]), "S")

        # ClassName -> identifier (just save class_name)
        if lhs == NTTitle.ClassName and not self.class_name:
            self.class_name = args[0].val

        # VarName -> identifier
        # ClassName -> identifier
        # SubroutineName -> identifier
        if lhs in (NTTitle.ClassName, NTTitle.VarName, NTTitle.SubroutineName):
            return NonTerminal(
                NTTitle[lhs], self._get_start_token(args[0]), args[0].val
            )

        # ClassVarDecList -> ClassVarDec
        # ClassVarDecList -> ClassVarDecList ClassVarDec
        if lhs == NTTitle.ClassVarDecList:  # symbols already defined
            return NonTerminal(NTTitle.ClassVarDecList, self._get_start_token(args[0]))

        # ClassVarDec -> 'static' Type VarNameList ';'
        # ClassVarDec -> 'field' Type VarNameList ';'
        if lhs == NTTitle.ClassVarDec:
            kind = SymbolKind.STATIC if args[0].val == "static" else SymbolKind.FIELD
            v_type = args[1].get_val()
            for name in args[2].get_var_list():
                self.symbols.define(name, v_type, kind)
            return NTwithVarList(
                NTTitle.ClassVarDec,
                self._get_start_token(args[0]),
                v_type,
                var_list=args[2].get_var_list(),
            )

        # Type -> 'int'
        # Type -> 'char'
        # Type -> 'boolean'
        # Type -> ClassName
        if lhs == NTTitle.Type:
            if not isinstance(args[0], Token):
                return NonTerminal(
                    NTTitle.ClassName, self._get_start_token(args[0]), args[0].val
                )
            return NonTerminal(
                NTTitle.Type, self._get_start_token(args[0]), VarTypes[args[0].val]
            )

        # VarNameList -> VarName
        # VarNameList -> VarNameList ',' VarName
        if lhs == NTTitle.VarNameList:
            if len(args) == 1:
                return NTwithVarList(
                    NTTitle.VarNameList,
                    self._get_start_token(args[0]),
                    VarTypes.unknown,
                    var_list=[args[0].val],
                )
            args[0].var_list.append(args[2].val)
            return args[0]

        # TypedVarNameList -> Type VarName
        # TypedVarNameList -> TypedVarNameList ',' Type VarName
        if lhs == NTTitle.TypedVarNameList:
            if len(args) == 2:
                return NTwithTypedVarList(
                    NTTitle.TypedVarNameList,
                    self._get_start_token(args[0]),
                    typed_var_list=[(args[0].get_val(), args[1].val)],
                )
            args[0].typed_var_list.append((args[2].get_val(), args[3].val))
            return args[0]

        # ParameterList -> '(' ')'
        # ParameterList -> '(' TypedVarNameList ')'
        if lhs == NTTitle.ParameterList:
            if len(args) == 2:
                return NonTerminal(
                    NTTitle.ParameterList, self._get_start_token(args[0])
                )
            for p_type, p_name in args[1].get_typed_var_list():
                self.symbols.define(p_name, p_type, SymbolKind.ARG)
            return NonTerminal(NTTitle.ParameterList, self._get_start_token(args[0]))

        # SubroutineDecList -> SubroutineDec
        # SubroutineDecList -> SubroutineDecList SubroutineDec
        if lhs == NTTitle.SubroutineDecList:
            writable = NTwithCode(
                NTTitle.SubroutineDecList, self._get_start_token(args[0])
            )
            writable.extend(args[0].vm)
            if len(args) == 2:
                writable.extend(args[1].vm)
            return writable

        # VarDeclaration -> 'var' Type VarNameList ';'
        if lhs == NTTitle.VarDeclaration:
            v_type = args[1].get_val()
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
        if lhs == NTTitle.VarDeclarationList:  # in subroutine
            return NonTerminal(
                NTTitle.VarDeclarationList, self._get_start_token(args[0])
            )

        # SubroutineBody -> '{' VarDeclarationList StatementsList '}'
        # SubroutineBody -> '{' VarDeclarationList '}'
        # SubroutineBody -> '{' StatementsList '}'
        # SubroutineBody -> '{' '}'
        if lhs == NTTitle.SubroutineBody:
            writable = NTwithCode(
                NTTitle.SubroutineBody, self._get_start_token(args[0])
            )
            for arg in args:
                if isinstance(arg, NTwithCode) and arg.title == NTTitle.StatementsList:
                    writable.extend(arg.vm)
            return writable

        # SubroutineDec -> 'constructor' 'void' SubroutineName ParameterList SubroutineBody
        # SubroutineDec -> 'constructor' Type SubroutineName ParameterList SubroutineBody
        # SubroutineDec -> 'function' 'void' SubroutineName ParameterList SubroutineBody
        # SubroutineDec -> 'function' Type SubroutineName ParameterList SubroutineBody
        # SubroutineDec -> 'method' 'void' SubroutineName ParameterList SubroutineBody
        # SubroutineDec -> 'method' Type SubroutineName ParameterList SubroutineBody
        if lhs == NTTitle.SubroutineDec:  # TODO: check
            writable = NTwithCode(NTTitle.SubroutineDec, self._get_start_token(args[0]))
            s_kind = args[0].val
            # s_type = args[1].val
            s_name = args[2].val
            n_locals = self.symbols.var_count(SymbolKind.VAR)
            writable.vm.write_function(f"{self.class_name}.{s_name}", n_locals)

            if s_kind == "constructor":  # TODO: can be constructor void?
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
        if (
            lhs == NTTitle.LetStatement
        ):  # Expression already calculated and placed on stack
            writable = NTwithCode(NTTitle.LetStatement, self._get_start_token(args[0]))
            if len(args) == 5:  # let VarName = Expression ;
                writable.extend(args[3].vm)
                kind = self.symbols.kind_of(args[1])
                idx = self.symbols.index_of(args[1])
                writable.vm.write_pop(kind, idx)
            else:  # let VarName [ Expression ] = Expression ;
                kind, index = self.symbols[args[1]]
                writable.vm.write_push(kind, index)
                writable.extend(args[3].vm)
                writable.vm.write_arithmetic("add")
                writable.vm.write_pop("pointer", 1)
                writable.extend(args[6].vm)
                writable.vm.write_pop("that", 0)  # TODO: check array using
            return writable

        # DoStatement -> 'do' SubroutineCall ';'
        if lhs == NTTitle.DoStatement:
            writable = NTwithCode(NTTitle.DoStatement, self._get_start_token(args[0]))
            writable.extend(args[1].vm)
            return writable

        # ReturnStatement -> 'return' ';'
        # ReturnStatement -> 'return' Expression ';'
        if lhs == NTTitle.ReturnStatement:
            writable = NTwithCode(
                NTTitle.ReturnStatement, self._get_start_token(args[0])
            )
            if len(args) == 2:
                writable.vm.write_push("constant", 0)
            else:
                writable.extend(args[1].vm)
            writable.vm.write_return()
            return writable

        # Expression -> Term
        # Expression -> UnaryOperationList Term
        # Expression -> Expression Operation Term
        # Expression -> Expression Operation UnaryOperationList Term
        if lhs == NTTitle.Expression:
            writable = NTwithCode(NTTitle.Expression, self._get_start_token(args[0]))
            if len(args) == 1:
                writable.extend(args[0].vm)
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

        # SubroutineCall -> SubroutineName '(' ExpressionList ')'
        # SubroutineCall -> SubroutineName '(' ')'
        # SubroutineCall -> ClassName '.' SubroutineName '(' ExpressionList ')'
        # SubroutineCall -> VarName '.' SubroutineName '(' ExpressionList ')'
        # SubroutineCall -> ClassName '.' SubroutineName '(' ')'
        # SubroutineCall -> VarName '.' SubroutineName '(' ')'
        if (
            lhs == NTTitle.SubroutineCall
        ):  # TODO: we need to understand, method/constructor/other func we have
            writable = NTwithCode(
                NTTitle.SubroutineCall, self._get_start_token(args[0])
            )

            if len(args) >= 2 and isinstance(args[1], Token) and args[1].val == ".":
                prefix_node = args[0]  # NonTerminal (ClassName или VarName)
                sub_name_node = args[2]  # NonTerminal SubroutineName
                sub_name = sub_name_node.val

                if prefix_node.title == NTTitle.VarName:
                    name = prefix_node.val
                    # Проверяем, существует ли переменная с таким именем
                    if self.symbols.contains(name):
                        # Это действительно объект: obj.method(...)
                        var_type = self.symbols.type_of(prefix_node)
                        full_name = f"{var_type}.{sub_name}"
                        sig = self.subroutine_table.get(full_name)
                        if sig is None:
                            raise ErrUnknownFunc(full_name)

                        kind = self.symbols.kind_of(prefix_node)
                        idx = self.symbols.index_of(prefix_node)
                        writable.vm.write_push(kind, idx)

                        if (
                            len(args) == 6
                        ):  # VarName '.' SubroutineName '(' ExpressionList ')'
                            writable.extend(args[4].vm)

                        # Для метода передаём неявный this
                        n_args = (
                            sig.nargs + 1
                            if sig.kind == SubroutineKind.method
                            else sig.nargs
                        )
                        writable.vm.write_call(full_name, n_args)
                    else:
                        # Переменной нет – значит, это ClassName
                        class_name = name
                        full_name = f"{class_name}.{sub_name}"
                        sig = self.subroutine_table.get(full_name)
                        if sig is None:
                            raise ErrUnknownFunc(full_name)

                        if len(args) == 6:
                            writable.extend(args[4].vm)

                        writable.vm.write_call(full_name, sig.nargs)

                else:  # prefix_node.title == NTTitle.ClassName
                    class_name = prefix_node.val
                    full_name = f"{class_name}.{sub_name}"
                    sig = self.subroutine_table.get(full_name)
                    if sig is None:
                        raise ErrUnknownFunc(full_name)

                    if len(args) == 6:
                        writable.extend(args[4].vm)

                    writable.vm.write_call(full_name, sig.nargs)

            else:
                # Вызов без точки: SubroutineName (в текущем классе)
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
                    writable.vm.write_call(full_name, sig.nargs + 1)
                else:
                    if len(args) == 4:
                        writable.extend(args[2].vm)
                    writable.vm.write_call(full_name, sig.nargs)

            return writable

        # ExpressionList -> Expression
        # ExpressionList -> ExpressionList ',' Expression
        if lhs == NTTitle.ExpressionList:
            writable = NTwithCode(
                NTTitle.ExpressionList, self._get_start_token(args[0])
            )
            writable.extend(args[0].vm)
            if len(args) == 3:
                writable.extend(args[2].vm)
            return writable

        # UnaryOperationList -> UnaryOperation
        # UnaryOperationList -> UnaryOperationList UnaryOperation
        if lhs == NTTitle.UnaryOperationList:
            writable = NTwithCode(
                NTTitle.UnaryOperationList, self._get_start_token(args[0])
            )
            writable.extend(args[0].vm)
            if len(args) == 2:
                writable.extend(args[1].vm)
            return writable

        # UnaryOperation -> '-'
        # UnaryOperation -> '~'
        if lhs == NTTitle.UnaryOperation:
            writable = NTwithCode(
                NTTitle.UnaryOperation, self._get_start_token(args[0])
            )
            if args[0].val == "-":
                writable.vm.write_arithmetic("neg")
            else:
                writable.vm.write_arithmetic("not")
            return writable

        # Operation -> Token()...
        if lhs == NTTitle.Operation:
            writable = NTwithCode(NTTitle.Operation, self._get_start_token(args[0]))
            self._write_op_to_writer(args[0].val, writable.vm)
            return writable

        # IfHeader -> 'if' '(' Expression ')'
        if lhs == NTTitle.IfHeader:
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
        if lhs == NTTitle.ElsePart:
            writable = NTwithCode(NTTitle.ElsePart, self._get_start_token(args[0]))
            if len(args) == 4:
                writable.extend(args[2].vm)
            return writable

        # IfStatement -> IfHeader '{' StatementsList '}'
        # IfStatement -> IfHeader '{' StatementsList '}' ElsePart
        # IfStatement -> IfHeader '{' '}'
        # IfStatement -> IfHeader '{' '}' ElsePart
        if lhs == NTTitle.IfStatement:
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

        # WhileHeader -> 'while'
        if lhs == NTTitle.WhileHeader:
            idx = self.label_idx
            self.label_idx += 1
            writable = NTwithCode(
                NTTitle.WhileHeader,
                self._get_start_token(args[0]),
                l1=f"WHILE_EXP{idx}",
            )
            writable.vm.write_label(writable.kwargs["l1"])
            return writable

        # WhileCondition -> WhileHeader '(' Expression ')'
        if lhs == NTTitle.WhileCondition:
            idx = self.label_idx
            self.label_idx += 1
            writable = NTwithCode(
                NTTitle.WhileCondition,
                self._get_start_token(args[0]),
                l2=f"WHILE_EXP{idx}",
                **args[0].kwargs,
            )
            writable.extend(args[0].vm)
            writable.extend(args[2].vm)
            writable.vm.write_arithmetic("not")
            writable.vm.write_if(writable.kwargs["l2"])
            return writable

        # WhileStatement -> WhileCondition '{' StatementsList '}'
        # WhileStatement -> WhileCondition '{' '}'
        if lhs == NTTitle.WhileStatement:
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
        if lhs == NTTitle.StatementsList:
            writable = NTwithCode(
                NTTitle.StatementsList, self._get_start_token(args[0])
            )
            writable.extend(args[0].vm)
            if len(args) == 2:
                writable.extend(args[1].vm)
            return writable

        # Statement -> LetStatement
        # Statement -> IfStatement
        # Statement -> WhileStatement
        # Statement -> DoStatement
        # Statement -> ReturnStatement
        if lhs == NTTitle.Statement:
            writable = NTwithCode(NTTitle.Statement, self._get_start_token(args[0]))
            writable.extend(args[0].vm)
            return writable

        # KeywordConstant -> 'true'
        # KeywordConstant -> 'false'
        # KeywordConstant -> 'null'
        # KeywordConstant -> 'this'
        if lhs == NTTitle.KeywordConstant:
            writable = NTwithCode(
                NTTitle.KeywordConstant, self._get_start_token(args[0])
            )
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
        if lhs == "Term":
            writable = (
                NTwithCode(NTTitle.Term, self._get_start_token(args[0]))
                if isinstance(args[0], Token)
                else NTwithCode(NTTitle.Term, args[0].start_token)
            )
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
            elif (
                len(args) == 4
            ):  # TODO: Array implementation. Is current version  implemented correctly?
                kind, index = self.symbols[args[0]]
                writable.vm.write_push(kind, index)
                writable.extend(args[2].vm)  # Expression
                writable.vm.write_arithmetic("add")
                writable.vm.write_pop("pointer", 1)
                writable.vm.write_push("that", 0)
            elif len(args) == 3:
                writable.extend(args[1].vm)
            elif args[0].title == NTTitle.VarName:
                kind, index = self.symbols[args[0]]
                writable.vm.write_push(kind, index)
            elif args[0].title == NTTitle.SubroutineCall:  # TODO: subroutine calling
                writable.extend(args[0].vm)
            return writable

        raise SyntaxError()

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
