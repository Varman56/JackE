import csv

from compiler.source.grammar.automata import Automata


class SLRParser:
    def __init__(self, filename="grammar.slr", outfile="jack_slr_table.csv"):
        self.automata = Automata(filename)
        self.reader = self.automata.reader
        self.action_table = {}
        self.goto_table = {}
        self.errors = []
        self.build_tables()
        self.save_table_to_csv(outfile)

    def build_tables(self):
        for i, state in enumerate(self.automata.states):
            for item in state:
                if item.next_symbol is None:
                    if item.rule.left == self.reader.rules[0].left:
                        self.set_action(i, '$', "ACC")
                    else:
                        follow_set = self.automata.follow.get(item.rule.left, set())
                        for terminal in follow_set:
                            self.set_action(i, terminal, f"R{item.rule.id}")

                else:
                    symbol = item.next_symbol
                    next_idx = self.automata.transitions.get((i, symbol))

                    if next_idx is not None:
                        if symbol in self.reader.terminals:
                            self.set_action(i, symbol, f"S{next_idx}")
                        else:
                            self.goto_table[(i, symbol)] = next_idx

    def set_action(self, state_idx, terminal, action):
        current = self.action_table.get((state_idx, terminal))
        if current and current != action:
            self.errors.append(f"Конфликт в состоянии {state_idx} по символу {terminal}: {current} vs {action}")
            if current.startswith('S') and action.startswith('R'):
                return
        self.action_table[(state_idx, terminal)] = action

    def save_table_to_csv(self, filename):
        terminals = sorted(list(self.reader.terminals))
        non_terminals = sorted(list(self.reader.non_terminals - {self.reader.rules[0].left}))

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ["State"] + terminals + non_terminals
            writer.writerow(header)

            for i in range(len(self.automata.states)):
                row = [i]
                for t in terminals:
                    row.append(self.action_table.get((i, t), ""))
                for nt in non_terminals:
                    row.append(self.goto_table.get((i, nt), ""))
                writer.writerow(row)
