from compiler.source.code_generator.non_terminal_title import NTTitle
from compiler.source.code_generator.var_types import VarTypes
from compiler.source.code_generator.vm_writer import VMWriter
from compiler.source.tokenizer.token import Token


class NonTerminal:
    def __init__(self, title: NTTitle, start_token: Token, val="", **kwargs):
        self.title = title
        self.start_token = start_token
        self.val = val
        self.kwargs = kwargs

    def __repr__(self):
        return f"{self.title} ({self.start_token.row} {self.start_token.col})"

    def get_kwargs(self):
        return self.kwargs


class NTwithTypedVarList(NonTerminal):  # (type name, type name, ...)
    def __init__(self, title, start_token, val="", typed_var_list=[], **kwargs):
        super().__init__(title, start_token, val, **kwargs)
        self.typed_var_list = typed_var_list

    def get_typed_var_list(self):
        return self.typed_var_list


class NTwithVarList(NonTerminal):
    def __init__(
        self, title, start_token, var_type: VarTypes, val="", var_list=[], **kwargs
    ):
        super().__init__(title, start_token, val, **kwargs)
        self.var_list = var_list
        self.var_type = var_type

    def get_var_list(self):
        return self.var_list

    def get_type(self):
        return self.var_type


# class NTwithExpression(NonTerminal):
#     def __init__(self, title, start_token, res_type: VarTypes, val="", **kwargs):
#         super().__init__(title, start_token, val, **kwargs)
#         self.res_type = res_type
#
#     def get_type(self):
#         return self.res_type
#
#     def check_bin_op_ability(self, bin_op, other):  # TODO: type checking
#         pass
#
#     def check_un_op(self, un_op):
#         pass


class NTwithCode(NonTerminal):
    def __init__(self, title, start_token, **kwargs):
        super().__init__(title, start_token, **kwargs)
        self.vm = VMWriter()

    def get_output(self):
        return self.vm.output

    def extend(self, other_vm: VMWriter):
        self.vm.output.extend(other_vm.get_collected())
