class Rule:
    """Класс для правил грамматики. Хранит левую и правую часть правишла, и его id"""

    def __init__(self, left, right, rule_id):
        self.left = left
        self.right = right
        self.id = rule_id

    def __repr__(self):
        return f"{self.left} -> {' '.join(self.right)}"

    def __eq__(self, other):
        return isinstance(other, Rule) and self.id == other.id
