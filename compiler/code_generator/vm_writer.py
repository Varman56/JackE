from compiler.code_generator.symbol import SymbolKind


class VMWriter:
    """Класс для записпи команд виртуальной машины в виде списка строк"""

    def __init__(self) -> None:
        self.output: list[str] = []

    def write_push(self, segment: SymbolKind | str, index: int | str) -> None:
        self.output.append(f"push {segment} {index}")

    def write_pop(self, segment: SymbolKind | str, index: int | str) -> None:
        self.output.append(f"pop {segment} {index}")

    def write_arithmetic(self, command: str) -> None:
        # add, sub, neg, eq, gt, lt, and, or, not
        self.output.append(command.lower())

    def write_label(self, label: str) -> None:
        self.output.append(f"label {label}")

    def write_goto(self, label: str) -> None:
        self.output.append(f"goto {label}")

    def write_if(self, label: str) -> None:
        self.output.append(f"if-goto {label}")

    def write_call(self, name: str, n_args: int) -> None:
        self.output.append(f"call {name} {n_args}")

    def write_function(self, name: str, n_locals: int) -> None:
        self.output.append(f"function {name} {n_locals}")

    def write_return(self) -> None:
        self.output.append("return")

    @property
    def get_collected(self) -> list[str]:
        return self.output
