class ErrUnknownSymbol(RuntimeError):
    def __init__(self, pos_x, pos_y):
        super().__init__(f"Unknown variable at {pos_x}:{pos_y}")