class ErrUnknownSymbol(RuntimeError):
    def __init__(self, pos_x: int, pos_y: int) -> None:
        super().__init__(f"Unknown variable at {pos_x}:{pos_y}")


class ErrUnknownFunc(NameError):
    def __init__(self, full_name: str, pos_x: int, pos_y: int) -> None:
        super().__init__(
            f"Subroutine '{full_name}' on {pos_x}:{pos_y} not found in global table"
        )
