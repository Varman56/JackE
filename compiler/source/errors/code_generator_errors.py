class ErrUnknownSymbol(RuntimeError):
    def __init__(self, pos_x, pos_y):
        super().__init__(f"Unknown variable at {pos_x}:{pos_y}")


class ErrUnknownFunc(NameError):
    def __init__(self, full_name):
        super().__init__(f"Subroutine '{full_name}' not found in global table")
