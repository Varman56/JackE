from compiler.source.precompile.subroutine_kind import SubroutineKind


class Subroutine:
    def __init__(
        self, class_name, sub_name, kind: SubroutineKind, params_count, res_type
    ):
        # self.arg_types = [] # TODO: type checking
        self.class_name = class_name
        self.sub_name = sub_name
        self.kind = kind
        self.nargs = params_count
        self.rtype = res_type

    def get_nargs(self):
        if self.kind == SubroutineKind.method:
            return self.nargs + 1
        return self.nargs

    def get_full_name(self):
        return f"{self.class_name}.{self.sub_name}"

    def __repr__(self):
        return f"{self.kind.name} {self.get_full_name()}({self.nargs}) {self.rtype}"
