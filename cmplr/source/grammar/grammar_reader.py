from grammar.rule import Rule


class GrammarReader:
    def __init__(self, filename="grammar"):
        self.filename = filename
        self.rules = []
        self.terminals = set()
        self.non_terminals = set()
        self.read()

    def read(self):
        rule_counter = 0
        with open(self.filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '->' not in line:
                    continue

                lhs_str, rhs_str = line.split('->')
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

        self.terminals.add('$')
