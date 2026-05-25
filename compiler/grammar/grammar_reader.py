from compiler.grammar.rule import Rule


class GrammarReader:
    """Класс для чтения файла грамматики и сохранения информации о ней

     Аргументы:
    - filename: Путь до файла грамматики"""

    def __init__(self, filename: str):
        self.filename = filename
        self.rules: list[Rule] = []
        self.terminals: set[str] = set()
        self.non_terminals: set[str] = set()
        self._read()

    def _read(self) -> None:
        """Чтение файла файла грамматики"""
        rule_counter = 0
        with open(self.filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "->" not in line:
                    continue

                lhs_str, rhs_str = line.split("->")
                lhs = lhs_str.strip()

                raw_rhs_symbols = rhs_str.strip().split()
                clean_rhs = []
                for symbol in raw_rhs_symbols:
                    clean_symbol = symbol.strip("'\"")
                    if clean_symbol:
                        clean_rhs.append(clean_symbol)

                new_rule = Rule(lhs, clean_rhs, rule_counter)
                self.rules.append(new_rule)
                self.non_terminals.add(lhs)
                rule_counter += 1

        for rule in self.rules:
            for symbol in rule.right:
                if symbol not in self.non_terminals:
                    self.terminals.add(symbol)

        self.terminals.add("EOF")
