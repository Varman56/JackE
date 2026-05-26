from compiler.code_generator.non_terminal_title import NTTitle
from compiler.code_generator.var_types import VarTypes
from compiler.code_generator.vm_writer import VMWriter
from compiler.tokenizer.token import Token


class NonTerminal:
    """Класс нетерминала, хранит дополнительную информацию

     Аргументы:
    - title: NTTitle - заголовок нетерминала
    - start_token: Токен с которого начинается нетерминал, нужен для вывода ошибки
    - val: Значение, которое хранит в себе нетерминал
    - kwargs: Дополнительные аргументы"""

    def __init__(
        self, title: NTTitle, start_token: Token, val: str = "", **kwargs
    ) -> None:
        self.title = title
        self.start_token = start_token
        self.val = val
        self.kwargs = kwargs
        self.vm = VMWriter()

    def __repr__(self) -> str:
        return f"{self.title} ({self.start_token.row} {self.start_token.col})"

    @property
    def get_typed_var_list(self) -> list[tuple[VarTypes | str, str]]:
        raise NotImplementedError("Use NTwithTypedVarList for get_typed_var_list using")

    @property
    def get_var_list(self) -> list[str]:
        raise NotImplementedError("Use NTwithVarList for get_var_list using")


class NTwithTypedVarList(NonTerminal):  # (type name, type name, ...)
    """Нетерминал с дополнительной информацией в виде списка переменных, где кадждая с определённым типом"""

    def __init__(
        self,
        title: NTTitle,
        start_token: Token,
        val: str = "",
        typed_var_list: list[tuple[VarTypes | str, str]] = [],
        **kwargs,
    ) -> None:
        super().__init__(title, start_token, val, **kwargs)
        self.typed_var_list = typed_var_list

    @property
    def get_typed_var_list(self) -> list[tuple[VarTypes | str, str]]:
        return self.typed_var_list


class NTwithVarList(NonTerminal):
    """Нетерминал с дополнительной информацией в виде списка переменных одного типа"""

    def __init__(
        self,
        title: NTTitle,
        start_token: Token,
        var_type: VarTypes | str,
        val: str = "",
        var_list: list[str] = [],
        **kwargs,
    ) -> None:
        super().__init__(title, start_token, val, **kwargs)
        self.var_list = var_list
        self.var_type = var_type

    @property
    def get_var_list(self) -> list[str]:
        return self.var_list


class NTwithCode(NonTerminal):
    """Нетерминал который сохраняет команды виртуальной машины"""

    def __init__(self, title: NTTitle, start_token: Token, **kwargs) -> None:
        super().__init__(title, start_token, **kwargs)
        self.vm = VMWriter()

    def get_output(self) -> list[str]:
        return self.vm.output

    def extend(self, other_vm: VMWriter) -> None:
        self.vm.output.extend(other_vm.get_collected)
