class Item:
    def __init__(self, rule, dot_pos):
        self.rule = rule
        self.dot_pos = dot_pos

    @property
    def next_symbol(self):
        if self.dot_pos < len(self.rule.right):
            return self.rule.right[self.dot_pos]
        return None

    def __repr__(self):
        rhs = list(self.rule.right)
        rhs.insert(self.dot_pos, "•")
        return f"{self.rule.left} -> {' '.join(rhs)}"
