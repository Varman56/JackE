from compiler.source.code_generator.non_terminal_title import NTTitle
from compiler.source.code_generator.var_types import VarTypes
from compiler.source.code_generator.vm_writer import VMWriter
from compiler.source.tokenizer.token import Token


class NonTerminal:
    """Класс нетерминала, хрнаит дополнительную информацию

     Аргументы:
    - title: NTTitle - заголовок нетерминала
    - start_token: Токен с которого начинается нетерминал, нужен для вывода ошибки
    - val: Значение, которое хранит в себе нетерминал
    - kwargs: Дополнительные аргументы"""

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
    """Нетерминал с дополнительной информацией в виде списка переменных, где кадждая с определённым типом"""

    def __init__(self, title, start_token, val="", typed_var_list=[], **kwargs):
        super().__init__(title, start_token, val, **kwargs)
        self.typed_var_list = typed_var_list

    def get_typed_var_list(self):
        return self.typed_var_list


class NTwithVarList(NonTerminal):
    """Нетерминал с дополнительной информацией в виде списка переменных одного типа"""

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


class NTwithCode(NonTerminal):
    """Нетерминал который сохраняет команды виртуальной машины"""

    def __init__(self, title, start_token, **kwargs):
        super().__init__(title, start_token, **kwargs)
        self.vm = VMWriter()

    def get_output(self):
        return self.vm.output

    def extend(self, other_vm: VMWriter):
        self.vm.output.extend(other_vm.get_collected())
