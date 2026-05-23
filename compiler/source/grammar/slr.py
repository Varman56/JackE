import csv

from compiler.source.grammar.automata import Automata


class SLRParser:
    """Класс для построения таблицы slr анализатора

     Аргументы:
    - filename: Путь до файла грамматики
    - outfile: Путь  куда будет сохранена таблица slr анализатора"""

    def __init__(self, filename="grammar.slr", outfile="jack_slr_table.csv"):
        self.automata = Automata(filename)
        self.reader = self.automata.reader
        self.action_table = {}
        self.goto_table = {}
        self.errors = []
        self.build_tables()
        self.save_table_to_csv(outfile)

    def build_tables(self):
        """Построение таблицы slr анализатора"""
        for i, state in enumerate(self.automata.states):
            for item in state:
                if item.next_symbol is None:
                    if item.rule.left == self.reader.rules[0].left:
                        self.set_action(i, "EOF", "ACC")
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

    def log_conflict(self, state_idx, terminal, existing_action, new_action):
        """Формаирование информации о конфликте в таблицу"""
        state = self.automata.states[state_idx]
        lines = list()
        lines.append(
            f"=== Конфликт в состоянии {state_idx} по символу '{terminal}' ==="
        )
        lines.append(f"Действия: {existing_action} vs {new_action}")

        if existing_action.startswith("S") and new_action.startswith("R"):
            lines.append("Тип: shift/reduce (оставлен shift)")
        elif existing_action.startswith("R") and new_action.startswith("S"):
            lines.append("Тип: shift/reduce (оставлен shift)")
        else:
            lines.append("Тип: reduce/reduce")

        lines.append("\nСостояние содержит пункты:")
        for item in state:
            lhs = item.rule.left
            rhs = item.rule.right
            dot = item.dot_pos
            before = rhs[:dot]
            after = rhs[dot:]
            rule_str = f"{lhs} -> {' '.join(before)} • {' '.join(after)}"
            if item.next_symbol is None:
                lines.append(f"  [R] {rule_str}  (правило {item.rule.id})")
            elif item.next_symbol == terminal:
                lines.append(f"  [S] {rule_str}  (shift по '{terminal}')")
            else:
                lines.append(f"      {rule_str}")

        lines.append("\nFOLLOW-множества нетерминалов, участвующих в свёртках:")
        for item in state:
            if item.next_symbol is None:
                lhs = item.rule.left
                f_set = self.automata.follow.get(lhs, set())
                lines.append(f"  FOLLOW({lhs}) = {{ {', '.join(sorted(f_set))} }}")

        lines.append("=============================================\n")
        return "\n".join(lines)

    def set_action(self, state_idx, terminal, action):
        """Сохранение действия по таблице"""
        current = self.action_table.get((state_idx, terminal))
        if current and current != action:
            conflict_msg = self.log_conflict(state_idx, terminal, current, action)
            self.errors.append(conflict_msg)
            if current.startswith("S") and action.startswith("R"):
                return
        self.action_table[(state_idx, terminal)] = action

    def save_table_to_csv(self, filename):
        """Сохранить таблицу в csv"""
        terminals = sorted(list(self.reader.terminals))
        non_terminals = sorted(
            list(self.reader.non_terminals - {self.reader.rules[0].left})
        )

        with open(filename, "w", newline="", encoding="utf-8") as f:
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
