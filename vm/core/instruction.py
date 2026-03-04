class Instruction:
    def __init__(self):
        pass


class Push(Instruction):
    def __init__(self, segment, index):
        super().__init__()
        self.segment = segment
        self.index = index


class Pop(Instruction):
    def __init__(self, segment, index):
        super().__init__()
        self.segment = segment
        self.index = index


class Arithmetic(Instruction):
    pass


class Add(Arithmetic):
    pass


class Sub(Arithmetic):
    pass


class Neg(Arithmetic):
    pass


class Logical(Instruction):
    pass


class And(Logical):
    pass


class Or(Logical):
    pass


class Not(Logical):
    pass


class Comparison(Instruction):
    pass


class Eq(Comparison):
    pass


class Gt(Comparison):
    pass


class Lt(Comparison):
    pass
