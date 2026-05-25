class Rule:
    """Класс для правил грамматики. Хранит левую и правую часть правишла, и его id"""

    def __init__(self, left: str, right: list[str], rule_id: int) -> None:
        self.left = left
        self.right = right
        self.id = rule_id

    def __repr__(self) -> str:
        return f"{self.left} -> {' '.join(self.right)}"
