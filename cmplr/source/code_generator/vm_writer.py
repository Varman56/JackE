class VMWriter:
    def __init__(self):
        self.output = []

    def write_push(self, segment, index):
        # segment может быть строкой или SymbolKind.value
        seg = segment.value if hasattr(segment, 'value') else segment
        self.output.append(f"push {seg} {index}")

    def write_pop(self, segment, index):
        seg = segment.value if hasattr(segment, 'value') else segment
        self.output.append(f"pop {seg} {index}")

    def write_arithmetic(self, command):
        # add, sub, neg, eq, gt, lt, and, or, not
        self.output.append(command.lower())

    def write_label(self, label):
        self.output.append(f"label {label}")

    def write_goto(self, label):
        self.output.append(f"goto {label}")

    def write_if(self, label):
        self.output.append(f"if-goto {label}")

    def write_call(self, name, n_args):
        self.output.append(f"call {name} {n_args}")

    def write_function(self, name, n_locals):
        self.output.append(f"function {name} {n_locals}")

    def write_return(self):
        self.output.append("return")

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write("\n".join(self.output) + "\n")