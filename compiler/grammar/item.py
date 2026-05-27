from compiler.grammar.rule import Rule


class Item:
    """Класс для пункта грамматики. Хрнаит правило и позицию маркера"""

    def __init__(self, rule: Rule, dot_pos: int):
        self.rule = rule
        self.dot_pos = dot_pos

    @property
    def next_symbol(self) -> str | None:
        if self.dot_pos < len(self.rule.right):
            return self.rule.right[self.dot_pos]
        return None

    def __repr__(self) -> str:
        rhs = list(self.rule.right)
        rhs.insert(self.dot_pos, "•")
        return f"{self.rule.left} -> {' '.join(rhs)}"
